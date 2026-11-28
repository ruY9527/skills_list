(function () {
  'use strict';

  const skills = Array.isArray(window.SKILLS_DATA) ? window.SKILLS_DATA : [];
  const categories = Array.isArray(window.CATEGORIES_DATA) ? window.CATEGORIES_DATA : [];
  const site = window.SITE_DATA || { scenarios: [], faqs: [], globalInstall: {}, networkConfig: {} };
  const repoUrl = 'https://github.com/ruY9527/skills_list';
  const iconAliases = { lightbulb: 'compass', wrench: 'code', shield: 'review', spark: 'spark' };
  const kindLabels = { skill: '技能定义', user: '使用指南', script: '脚本', reference: '知识库', example: '结构样例' };
  const workflows = categories.filter((category) => category.hasWorkflow).map((category) => ({
    category,
    skills: skills.filter((skill) => skill.category === category.id && Number.isFinite(skill.stage))
      .sort((a, b) => a.stage - b.stage)
  })).filter((workflow) => workflow.skills.length > 0);
  const state = {
    activeWorkflow: workflows.length ? workflows[0].category.id : null,
    activeStageId: workflows.length ? workflows[0].skills[0].id : null,
    activeCategory: 'all',
    currentSkill: null,
    lastFocused: null,
    suppressHashSync: false,
    toastTimer: null
  };
  const copyTimers = new WeakMap();

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));
  const asArray = (value) => Array.isArray(value) ? value : [];

  function escapeHtml(value) {
    return String(value ?? '')
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function icon(name, className = '') {
    const resolved = iconAliases[name] || name || 'spark';
    return `<svg class="icon ${className}" aria-hidden="true"><use href="#i-${escapeHtml(resolved)}"></use></svg>`;
  }

  function copyButton(targetId, label = '复制') {
    return `<button class="copy-button" type="button" data-copy-target="${escapeHtml(targetId)}" aria-label="${escapeHtml(label)}">
      ${icon('copy')}<span class="copy-label">${escapeHtml(label)}</span></button>`;
  }

  function encodedRepoPath(skill) {
    return String(skill.repoPath).split('/').map(encodeURIComponent).join('/');
  }

  function sourceUrl(skill, filePath) {
    const encodedFile = filePath.split('/').map(encodeURIComponent).join('/');
    return `${repoUrl}/blob/main/${encodedRepoPath(skill)}/${encodedFile}`;
  }

  function treeUrl(skill) {
    return `${repoUrl}/tree/main/${encodedRepoPath(skill)}`;
  }

  function stageLabel(skill) {
    return Number.isFinite(skill.stage)
      ? `STAGE ${skill.stage} · ${skill.stageName}`
      : `INDEPENDENT · ${skill.stageName || '独立 Skill'}`;
  }

  function activeWorkflow() {
    return workflows.find((workflow) => workflow.category.id === state.activeWorkflow) || null;
  }

  function sectionHeading(number, title, subtitle) {
    return `<div class="detail-section-heading"><span class="detail-section-number">${number}</span>
      <div><h3>${escapeHtml(title)}</h3><p>${escapeHtml(subtitle)}</p></div></div>`;
  }

  function applyTheme(theme, persist = true) {
    const selected = theme === 'dark' ? 'dark' : 'light';
    document.documentElement.dataset.theme = selected;
    document.documentElement.style.colorScheme = selected;
    const themeColor = $('meta[name="theme-color"]');
    if (themeColor) themeColor.setAttribute('content', selected === 'dark' ? '#0e1120' : '#f7f8fc');
    const themeButton = $('#theme-toggle');
    const nextLabel = selected === 'dark' ? '切换浅色主题' : '切换深色主题';
    if (themeButton) {
      themeButton.setAttribute('aria-label', nextLabel);
      themeButton.setAttribute('title', nextLabel);
      themeButton.setAttribute('aria-pressed', String(selected === 'dark'));
    }
    const themeUse = $('#theme-icon');
    if (themeUse) themeUse.setAttribute('href', selected === 'dark' ? '#i-sun' : '#i-moon');
    if (persist) {
      try { window.localStorage.setItem('skills-site-theme', selected); } catch (error) { /* Storage is optional on file://. */ }
    }
  }

  function initTheme() {
    let saved = 'light';
    try { saved = window.localStorage.getItem('skills-site-theme') || 'light'; } catch (error) { saved = 'light'; }
    applyTheme(saved, false);
    $('#theme-toggle').addEventListener('click', () => {
      applyTheme(document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark');
    });
  }

  function renderHeroStats() {
    $('#stat-skill-count').textContent = skills.length;
    $('#stat-category-count').textContent = categories.length;
    $('#stat-script-count').textContent = skills.reduce((total, skill) => total + (Number(skill.scriptCount) || 0), 0);
    $('#scenario-count').textContent = `${asArray(site.scenarios).length} 个高频科研断点`;
    $('#faq-count').textContent = `${asArray(site.faqs).length} 条实用问答`;
    $('#workflow-cta').innerHTML = `${workflows.length ? '探索专题工作流' : '浏览技能目录'} ${icon('arrow-right')}`;
    $('#workflow-cta').setAttribute('href', workflows.length ? '#pipeline' : '#skills');
  }

  function renderConsole() {
    const workflow = activeWorkflow();
    const container = $('#console-stages');
    if (!workflow) {
      container.innerHTML = '<p class="console-empty">当前目录包含独立 Skill，没有绑定专题流程。</p>';
      $('#console-stage-count').textContent = 'INDEPENDENT';
      return;
    }
    $('#console-workflow-name').textContent = `${workflow.category.id}.workflow`;
    $('#console-workflow-title').textContent = `${workflow.category.name} research loop`;
    $('#console-stage-count').textContent = `${workflow.skills.length} STAGES`;
    container.innerHTML = workflow.skills.map((skill) => {
      const current = skill.id === state.activeStageId;
      return `<div class="console-stage${current ? ' is-current' : ''}">
        <span class="console-number">${String(skill.stage).padStart(2, '0')}</span>
        <span class="console-symbol">${icon(skill.icon)}</span>
        <span class="console-label"><strong>${escapeHtml(skill.stageName)} · ${escapeHtml(skill.alias)}</strong><span>${escapeHtml(skill.handoffLabel)}</span></span>
        <span class="console-state">${current ? 'ACTIVE' : 'READY'}</span></div>`;
    }).join('');
  }

  function renderWorkflowTabs() {
    const tabs = $('#workflow-tabs');
    tabs.hidden = workflows.length <= 1;
    tabs.innerHTML = workflows.map((workflow) => {
      const selected = workflow.category.id === state.activeWorkflow;
      return `<button class="workflow-tab${selected ? ' is-active' : ''}" id="workflow-tab-${escapeHtml(workflow.category.id)}"
        type="button" role="tab" aria-selected="${selected}" aria-controls="pipeline-flow" tabindex="${selected ? '0' : '-1'}"
        data-workflow="${escapeHtml(workflow.category.id)}">${icon('workflow')} ${escapeHtml(workflow.category.name)}
        <span>${workflow.skills.length} 环</span></button>`;
    }).join('');
  }

  function renderPipeline() {
    const workflow = activeWorkflow();
    $('#pipeline').hidden = !workflow;
    renderWorkflowTabs();
    if (!workflow) return;
    const flow = $('#pipeline-flow');
    flow.setAttribute('role', 'tabpanel');
    flow.setAttribute('aria-labelledby', `workflow-tab-${workflow.category.id}`);
    $('#pipeline-count').textContent = `${workflow.category.name} · ${workflow.skills.length} 个接力节点`;
    flow.innerHTML = workflow.skills.map((skill) => `
      <button class="stage-node" type="button" data-stage-select="${escapeHtml(skill.id)}" aria-pressed="false"
        aria-label="Stage ${skill.stage}：${escapeHtml(skill.stageName)}，${escapeHtml(skill.alias)}">
        <span class="stage-node-top"><span class="stage-index">STAGE ${skill.stage}</span><span class="stage-icon">${icon(skill.icon)}</span></span>
        <h3>${escapeHtml(skill.stageName)}</h3><p>${escapeHtml(skill.alias)}</p><span class="stage-relation">点击探索</span>
      </button>`).join('');
    selectStage(workflow.skills.some((skill) => skill.id === state.activeStageId) ? state.activeStageId : workflow.skills[0].id);
  }

  function relayCell(skill, type) {
    if (!skill) {
      return `<div class="relay-cell"><span class="relay-label">${type === 'previous' ? '上游输入' : '下游接力'}</span>
        <p class="relay-empty">${type === 'previous' ? '当前专题从这里开始。' : '完成本环后，可回到首个节点开启下一轮。'}</p></div>`;
    }
    const previous = type === 'previous';
    return `<div class="relay-cell"><span class="relay-label">${icon(previous ? 'arrow-left' : 'arrow-right')} ${previous ? '上游 · 提供输入' : '下游 · 接收产出'}</span>
      <h3>Stage ${skill.stage} · ${escapeHtml(skill.stageName)}</h3><p>${escapeHtml(previous ? skill.handoffLabel : skill.inputArtifact)}</p>
      <button class="relay-link" type="button" data-stage-select="${escapeHtml(skill.id)}">查看该节点 ${icon('arrow-right')}</button></div>`;
  }

  function selectStage(skillId) {
    const workflow = activeWorkflow();
    if (!workflow) return;
    const index = workflow.skills.findIndex((skill) => skill.id === skillId);
    if (index < 0) return;
    const skill = workflow.skills[index];
    state.activeStageId = skill.id;
    $$('.stage-node').forEach((node) => {
      const nodeIndex = workflow.skills.findIndex((item) => item.id === node.dataset.stageSelect);
      const distance = nodeIndex - index;
      node.classList.toggle('is-active', distance === 0);
      node.classList.toggle('is-upstream', distance === -1);
      node.classList.toggle('is-downstream', distance === 1);
      node.classList.toggle('is-unrelated', Math.abs(distance) > 1);
      node.setAttribute('aria-pressed', String(distance === 0));
      $('.stage-relation', node).textContent = distance === 0 ? '当前节点' : distance === -1 ? '上游 · 输入' : distance === 1 ? '下游 · 接力' : '点击探索';
    });
    $('#stage-summary').innerHTML = `${relayCell(workflow.skills[index - 1], 'previous')}
      <div class="relay-cell current"><span class="relay-label">${icon('zap')} 当前节点 · Stage ${skill.stage}</span>
        <h3>${escapeHtml(skill.alias)}</h3><p><strong>行动：</strong>${escapeHtml(skill.action)}</p>
        <p><strong>产出：</strong>${escapeHtml(skill.outputArtifact)}</p></div>${relayCell(workflow.skills[index + 1], 'next')}`;
    const detailButton = $('#stage-detail-button');
    detailButton.dataset.openSkill = skill.id;
    detailButton.innerHTML = `打开「${escapeHtml(skill.alias)}」完整指南 ${icon('arrow-up-right')}`;
    renderConsole();
  }

  function selectWorkflow(categoryId) {
    if (!workflows.some((workflow) => workflow.category.id === categoryId)) return;
    state.activeWorkflow = categoryId;
    state.activeStageId = activeWorkflow().skills[0].id;
    renderPipeline();
  }

  function renderScenarios() {
    $('#scenario-grid').innerHTML = asArray(site.scenarios).map((scenario) => `
      <button class="scenario-card" type="button" data-open-skill="${escapeHtml(scenario.skill)}" data-focus-generator="true">
        <span class="scenario-icon">${icon(scenario.icon)}</span><strong class="scenario-title">${escapeHtml(scenario.title)}</strong>
        <p>${escapeHtml(scenario.description)}</p><span class="scenario-action">直达${escapeHtml(scenario.keyword)}生成器 ${icon('arrow-right')}</span>
      </button>`).join('');
  }

  function skillSearchText(skill) {
    return [skill.id, skill.alias, skill.categoryName, skill.tagline, skill.description, skill.stageName,
      asArray(skill.tags).join(' '), asArray(skill.inputs).join(' '), asArray(skill.outputs).join(' '),
      asArray(skill.files).map((file) => `${file.path} ${file.desc}`).join(' ')
    ].join(' ').toLocaleLowerCase();
  }

  function renderCategoryFilters() {
    const filters = [{ id: 'all', name: '全部', skillCount: skills.length }, ...categories];
    $('#category-filters').innerHTML = filters.map((category) => {
      const selected = state.activeCategory === category.id;
      return `<button class="category-filter${selected ? ' is-active' : ''}" type="button" data-category-filter="${escapeHtml(category.id)}"
        aria-pressed="${selected}">${escapeHtml(category.name)} <span>${category.skillCount}</span></button>`;
    }).join('');
  }

  function renderSkills() {
    $('#skills-grid').innerHTML = skills.map((skill) => `
      <button class="skill-card" type="button" data-open-skill="${escapeHtml(skill.id)}" data-category="${escapeHtml(skill.category)}"
        data-search="${escapeHtml(skillSearchText(skill))}" aria-label="查看 ${escapeHtml(skill.alias)} 完整详情">
        <span class="skill-card-header"><span class="skill-stage">${escapeHtml(stageLabel(skill))}</span>
          <span class="skill-file-count">${icon('file')} ${skill.files.length} 个真实文件</span></span>
        <span class="skill-category">${icon('folder')} ${escapeHtml(skill.categoryName)}</span>
        <h3>${escapeHtml(skill.alias)}</h3><code class="skill-id">${escapeHtml(skill.id)}</code>
        <span class="skill-card-description">${escapeHtml(skill.tagline)}</span>
        <span class="tag-list">${asArray(skill.tags).map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`).join('')}</span>
        <span class="skill-card-footer"><span>What · Why · Workflow · How · Output · Next</span>${icon('arrow-up-right')}</span>
      </button>`).join('');
  }

  function codePanel({ id, title, windows, bash, compact = false }) {
    return `<div class="${compact ? 'inline-code-panel' : 'code-panel'}" data-code-switch><div class="code-toolbar">
      <span class="code-title">${icon('terminal')} ${escapeHtml(title)}</span><div class="os-tabs" role="tablist" aria-label="${escapeHtml(title)}操作系统">
        <button class="os-tab" type="button" role="tab" aria-selected="true" aria-controls="${id}-windows" data-os-tab="windows">PowerShell</button>
        <button class="os-tab" type="button" role="tab" aria-selected="false" aria-controls="${id}-bash" data-os-tab="bash" tabindex="-1">macOS &amp; Linux</button></div>
      ${copyButton(`${id}-windows`, '复制命令')}</div>
      <pre class="code-block" id="${id}-windows" data-os-panel="windows" role="tabpanel"><code>${escapeHtml(windows)}</code></pre>
      <pre class="code-block" id="${id}-bash" data-os-panel="bash" role="tabpanel" hidden><code>${escapeHtml(bash)}</code></pre></div>`;
  }

  function renderInstall() {
    const categoryCommands = categories.map((category) => `<div class="install-category-note">
      <span>按分类安装 · ${escapeHtml(category.name)}：</span>
      <code>.\\scripts\\install_skills.ps1 -Category ${escapeHtml(category.id)}</code>
      <code>./scripts/install_skills.sh --category ${escapeHtml(category.id)}</code></div>`).join('');
    $('#global-install-code').innerHTML = codePanel({
      id: 'global-install', title: `扁平安装 ${skills.length} 个目录化 Skill · 仓库根目录执行`,
      windows: site.globalInstall.windows, bash: site.globalInstall.bash
    }) + categoryCommands;
    $('#network-config-code').innerHTML = `<div data-code-switch><div class="code-toolbar"><span class="code-title">${icon('sliders')} config.toml</span>${copyButton('network-config', '复制配置')}</div>
      <pre class="code-block" id="network-config"><code>${escapeHtml(site.networkConfig.toml)}</code></pre></div>`;
  }

  function renderFaqs() {
    $('#faq-list').innerHTML = asArray(site.faqs).map((faq, index) => `
      <details class="faq-item"${index === 0 ? ' open' : ''}><summary>${escapeHtml(faq.q)}</summary>
        <div class="faq-answer"><p>${escapeHtml(faq.a)}</p></div></details>`).join('');
  }

  function renderPromptField(skill, field) {
    const id = `skill-${skill.id}-${field.key}`;
    if (field.type === 'checkboxes') {
      const defaults = asArray(field.default);
      return `<fieldset class="prompt-field prompt-field-checkbox" data-field-key="${field.key}" data-field-type="checkboxes" data-min="${field.min ?? 0}" data-max="${field.max ?? field.options.length}">
        <legend>${escapeHtml(field.label)}</legend><div class="checkbox-options">${field.options.map((option) => `
          <label class="checkbox-option"><input type="checkbox" name="${id}" value="${escapeHtml(option.value)}"${defaults.includes(option.value) ? ' checked' : ''}><span>${escapeHtml(option.label)}</span></label>`).join('')}</div>
        <p class="field-help">每次选择 ${field.min ?? 0}–${field.max ?? field.options.length} 项，保持任务边界清晰。</p></fieldset>`;
    }
    const common = `id="${id}" name="${id}" data-field-key="${field.key}"`;
    if (field.type === 'select') {
      return `<div class="prompt-field"><label for="${id}">${escapeHtml(field.label)}</label><select ${common}>${field.options.map((option) => {
        const value = typeof option === 'object' ? option.value : option;
        const label = typeof option === 'object' ? option.label : option;
        return `<option value="${escapeHtml(value)}"${value === field.default ? ' selected' : ''}>${escapeHtml(label)}</option>`;
      }).join('')}</select></div>`;
    }
    return `<div class="prompt-field"><label for="${id}">${escapeHtml(field.label)}</label><input type="${field.type}" ${common}
      value="${escapeHtml(field.default ?? '')}"${field.placeholder ? ` placeholder="${escapeHtml(field.placeholder)}"` : ''}
      ${field.min !== undefined ? ` min="${field.min}"` : ''}${field.max !== undefined ? ` max="${field.max}"` : ''}${field.type === 'text' ? ' spellcheck="false"' : ''}></div>`;
  }

  function defaultPromptValues(skill) {
    const values = {};
    asArray(skill.promptFields).forEach((field) => {
      values[field.key] = field.type === 'checkboxes' ? [...asArray(field.default)] : (field.default ?? '');
    });
    return values;
  }

  function renderPromptTemplate(skill, suppliedValues = {}) {
    const values = { ...defaultPromptValues(skill), ...suppliedValues };
    Object.entries(skill.promptComputed || {}).forEach(([key, rule]) => {
      const source = String(values[rule.field] ?? '');
      values[key] = Object.prototype.hasOwnProperty.call(rule.cases || {}, source) ? rule.cases[source] : (rule.default ?? '');
    });
    return String(skill.promptTemplate || '').replace(/\{\{\s*([\w-]+)(?::(plus|underscore))?\s*\}\}/g, (match, key, format) => {
      const field = asArray(skill.promptFields).find((item) => item.key === key);
      let value = values[key];
      if (Array.isArray(value)) return value.join(format === 'plus' ? ' + ' : format === 'underscore' ? '_' : ', ');
      if ((value === '' || value === null || value === undefined) && field) value = field.placeholder || field.default || '';
      return String(value ?? '');
    });
  }

  function renderDetail(skill) {
    const uid = skill.id;
    const nextSkill = skills.find((item) => item.id === skill.next);
    const files = asArray(skill.files).map((file) => `
      <a class="file-link" href="${sourceUrl(skill, file.path)}" target="_blank" rel="noopener noreferrer" title="查看 ${escapeHtml(skill.repoPath)}/${escapeHtml(file.path)} 源码">
        ${icon(file.kind === 'script' ? 'terminal' : file.kind === 'reference' ? 'book' : file.kind === 'example' ? 'eye' : 'file')}
        <span class="file-link-text"><code>${escapeHtml(file.path)}</code><small>${escapeHtml(kindLabels[file.kind] || file.kind)} · ${escapeHtml(file.desc)}</small></span>${icon('external')}</a>`).join('');
    const nextSection = nextSkill ? `
      <section class="detail-section" aria-labelledby="next-${uid}">${sectionHeading('06', '下游接力 · What’s Next', '把当前产物直接交给下一环，保持研究上下文连续')}
        <div class="downstream-card" id="next-${uid}"><div><p class="downstream-label">Stage ${nextSkill.stage} · ${escapeHtml(nextSkill.stageName)}</p><h4>${escapeHtml(nextSkill.alias)}</h4><p>${escapeHtml(skill.nextText)}</p></div>
          <button class="button button-primary" type="button" data-open-skill="${escapeHtml(nextSkill.id)}">接力到下一环 ${icon('arrow-right')}</button></div></section>` : `
      <section class="detail-section" aria-labelledby="next-${uid}">${sectionHeading('06', '分类归位 · Independent', '独立 Skill 不绑定专题流程，按当前任务直接使用')}
        <div class="downstream-card independent-card" id="next-${uid}"><div><p class="downstream-label">${escapeHtml(skill.categoryName)}</p><h4>按需调用，无需上下游产物</h4><p>该 Skill 保持独立入口，不会被强行加入其他分类的闭环。</p></div>
          <button class="button button-secondary" type="button" data-close-and-filter="${escapeHtml(skill.category)}">返回所属分类 ${icon('arrow-right')}</button></div></section>`;

    return `<div class="detail-hero"><div class="detail-hero-top"><div><span class="skill-stage">${escapeHtml(stageLabel(skill))}</span>
      <span class="detail-category">${icon('folder')} ${escapeHtml(skill.categoryName)}</span><h2 id="dialog-title">${escapeHtml(skill.alias)}</h2><code class="detail-id">${escapeHtml(skill.id)}</code></div></div>
      <p class="detail-tagline">${escapeHtml(skill.tagline)}</p><p class="detail-audience">${icon('users')}<span><strong>适合谁：</strong>${escapeHtml(skill.audience)}</span></p>
      <div class="detail-stats"><span class="detail-stat">${icon('workflow')} Phase 0–${skill.phases.length - 1}</span>
        <span class="detail-stat">${icon('terminal')} ${skill.scriptCount} 个真实脚本</span><span class="detail-stat">${icon('file')} ${skill.files.length} 个源文件直链</span></div></div>

    <section class="detail-section" aria-labelledby="what-${uid}">${sectionHeading('01', '是什么 · What', '明确输入、处理边界与可交付产物')}
      <p class="section-lead" id="what-${uid}">${escapeHtml(skill.description)}</p><div class="what-grid" style="margin-top: 18px">
        <div class="what-card"><h4>${icon('download')} 输入什么</h4><ul>${asArray(skill.inputs).map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul></div>
        <div class="what-card"><h4>${icon('upload')} 得到什么</h4><ul>${asArray(skill.outputs).map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul></div></div></section>

    <section class="detail-section" aria-labelledby="why-${uid}">${sectionHeading('02', '为什么要用 · Why', '从通用回答升级为有真实证据、可持久化的研究流程')}
      <div class="table-wrap"><table class="data-table comparison-table" id="why-${uid}"><thead><tr><th scope="col"><span class="pain-marker">${icon('x')} 普通问 AI / 人工推进</span></th><th scope="col"><span class="benefit-marker">${icon('check')} 使用本 Skill</span></th></tr></thead>
        <tbody>${asArray(skill.why).map((row) => `<tr><td>${escapeHtml(row.pain)}</td><td>${escapeHtml(row.benefit)}</td></tr>`).join('')}</tbody></table></div></section>

    <section class="detail-section" aria-labelledby="workflow-${uid}">${sectionHeading('03', '内部工作流 · Workflow', '阶段规则与仓库真实文件一一对应，点击文件查看源码')}
      <div class="phase-list" id="workflow-${uid}">${asArray(skill.phases).map((phase) => `<div class="phase-item"><span class="phase-name">${escapeHtml(phase.name)}</span><h4>${escapeHtml(phase.title)}</h4><p>${escapeHtml(phase.text)}</p></div>`).join('')}</div>
      <h4 class="file-inventory-title">${icon('folder')} 真实文件清单 · ${skill.files.length} 个</h4><div class="file-list">${files}</div></section>

    <section class="detail-section" aria-labelledby="usage-${uid}">${sectionHeading('04', '怎么用 · How to Use', '扁平安装后重启 Codex，用 $<skill-name> 或下面的完整 Prompt 触发')}
      <div class="usage-block" id="usage-${uid}"><div class="usage-block-title"><h4>${icon('terminal')} ① 安装本 Skill</h4><span>在 skills_list 仓库根目录执行</span></div>
        ${codePanel({ id: `install-${uid}`, title: skill.id, windows: skill.install.windows, bash: skill.install.bash, compact: true })}</div>
      <div class="usage-block"><div class="usage-block-title"><h4>${icon('sliders')} ② 生成本次任务 Prompt</h4><span>参数变化会实时更新</span></div>
        <form class="prompt-builder" id="prompt-builder" tabindex="-1" data-prompt-skill="${escapeHtml(uid)}">
          <div class="prompt-builder-header"><div><h4>${icon('zap')} 交互式 Prompt 生成器</h4><p>修改下方选项，即可拼出完整任务指令。</p></div><span class="live-badge">LIVE PREVIEW</span></div>
          <div class="prompt-fields">${asArray(skill.promptFields).map((field) => renderPromptField(skill, field)).join('')}</div>
          <div class="prompt-output-wrap"><div class="code-toolbar"><span class="code-title">${icon('message')} Ready for Codex</span>${copyButton('generated-prompt', '复制 Prompt')}</div><pre class="prompt-output" id="generated-prompt" tabindex="0"></pre></div>
          <p class="prompt-footnote">路径默认值是示例，请替换为本机真实文件。核心检索/台账脚本零外部依赖；指标出图按需使用 numpy/matplotlib。联网检索需开启 network_access。</p>
        </form></div></section>

    <section class="detail-section" aria-labelledby="output-${uid}">${sectionHeading('05', '预期产出预览 · Output', '展示真实产物结构；尖括号内容等待实际数据填充')}
      <h4 class="file-inventory-title" id="output-${uid}">${icon('eye')} ${escapeHtml(skill.preview.title)}</h4>
      <div class="table-wrap"><table class="data-table preview-table"><thead><tr>${skill.preview.headers.map((header) => `<th scope="col">${escapeHtml(header)}</th>`).join('')}</tr></thead>
        <tbody>${skill.preview.rows.map((row) => `<tr>${row.map((cell) => `<td>${escapeHtml(cell)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>
      <p class="preview-note">${icon('info')}<span>${escapeHtml(skill.preview.note)}</span></p></section>

    ${nextSection}<div class="dialog-footer"><span>由 SKILL.md、skill.meta.json 与真实目录自动构建 · 文件链接指向 main 分支</span>
      <a href="${treeUrl(skill)}" target="_blank" rel="noopener noreferrer">在 GitHub 查看整个 Skill ${icon('external')}</a></div>`;
  }

  function collectPromptValues(form, skill) {
    const values = {};
    asArray(skill.promptFields).forEach((field) => {
      if (field.type === 'checkboxes') {
        const group = $(`[data-field-key="${field.key}"]`, form);
        values[field.key] = $$('input[type="checkbox"]:checked', group).map((input) => input.value);
      } else {
        const input = $(`[data-field-key="${field.key}"]`, form);
        if (field.type === 'number') {
          const raw = Number(input.value);
          let value = Number.isFinite(raw) ? raw : Number(field.default);
          if (field.min !== undefined) value = Math.max(Number(field.min), value);
          if (field.max !== undefined) value = Math.min(Number(field.max), value);
          values[field.key] = value;
        } else values[field.key] = input.value.trim();
      }
    });
    return values;
  }

  function updatePrompt(form) {
    const skill = skills.find((item) => item.id === form.dataset.promptSkill);
    if (skill) $('#generated-prompt', form).textContent = renderPromptTemplate(skill, collectPromptValues(form, skill));
  }

  function updateHash(skillId) {
    window.history.pushState({ skill: skillId }, '', `${window.location.pathname}${window.location.search}#skill=${encodeURIComponent(skillId)}`);
  }

  function clearSkillHash() {
    if (window.location.hash.startsWith('#skill=')) window.history.replaceState(null, '', `${window.location.pathname}${window.location.search}`);
  }

  function openSkill(skillId, options = {}) {
    const skill = skills.find((item) => item.id === skillId);
    if (!skill) return;
    const targetWorkflow = workflows.find((workflow) => workflow.skills.some((item) => item.id === skillId));
    if (targetWorkflow && targetWorkflow.category.id !== state.activeWorkflow) {
      state.activeWorkflow = targetWorkflow.category.id;
      state.activeStageId = skillId;
      renderPipeline();
    }
    if (targetWorkflow) selectStage(skillId);
    const dialog = $('#skill-dialog');
    const alreadyOpen = dialog.open;
    if (!alreadyOpen) state.lastFocused = document.activeElement;
    state.currentSkill = skill.id;
    $('#dialog-current-title').textContent = skill.alias;
    $('#dialog-body').innerHTML = renderDetail(skill);
    if (!alreadyOpen) { dialog.showModal(); document.body.classList.add('modal-open'); }
    dialog.scrollTop = 0;
    updatePrompt($('#prompt-builder'));
    if (options.updateHash !== false && window.location.hash !== `#skill=${skill.id}`) updateHash(skill.id);
    window.requestAnimationFrame(() => {
      if (options.focusGenerator) {
        const builder = $('#prompt-builder');
        builder.scrollIntoView({ behavior: 'smooth', block: 'center' });
        builder.classList.add('is-targeted');
        builder.focus({ preventScroll: true });
        window.setTimeout(() => builder.classList.remove('is-targeted'), 1300);
      } else $('#dialog-close').focus({ preventScroll: true });
    });
  }

  function closeSkill() {
    const dialog = $('#skill-dialog');
    if (dialog.open) dialog.close();
  }

  function handleHash() {
    const hash = window.location.hash;
    if (hash.startsWith('#skill=')) {
      let skillId = '';
      try { skillId = decodeURIComponent(hash.slice(7)); } catch (error) { skillId = ''; }
      if (skills.some((skill) => skill.id === skillId)) {
        if (state.currentSkill !== skillId || !$('#skill-dialog').open) openSkill(skillId, { updateHash: false });
        return;
      }
    }
    if ($('#skill-dialog').open) { state.suppressHashSync = true; closeSkill(); }
  }

  function filterSkills() {
    const query = $('#skill-search').value.trim().toLocaleLowerCase();
    let visible = 0;
    $$('.skill-card').forEach((card) => {
      const matchesCategory = state.activeCategory === 'all' || card.dataset.category === state.activeCategory;
      const matchesQuery = !query || card.dataset.search.includes(query);
      card.hidden = !(matchesCategory && matchesQuery);
      if (matchesCategory && matchesQuery) visible += 1;
    });
    $('#skills-empty').hidden = visible !== 0;
    $('#skills-grid').hidden = visible === 0;
    $('#clear-search').hidden = !query && state.activeCategory === 'all';
    const category = categories.find((item) => item.id === state.activeCategory);
    $('#skill-count').textContent = `${visible} / ${skills.length} 个 Skill${category ? ` · ${category.name}` : ' · 全部分类'}`;
  }

  function clearFilters() {
    $('#skill-search').value = '';
    state.activeCategory = 'all';
    renderCategoryFilters();
    filterSkills();
  }

  function switchOs(tab) {
    const panel = tab.closest('[data-code-switch]');
    const selectedOs = tab.dataset.osTab;
    $$('[data-os-tab]', panel).forEach((button) => {
      const active = button === tab;
      button.setAttribute('aria-selected', String(active));
      button.tabIndex = active ? 0 : -1;
    });
    $$('[data-os-panel]', panel).forEach((code) => { code.hidden = code.dataset.osPanel !== selectedOs; });
    const copy = $('[data-copy-target]', panel);
    if (copy) copy.dataset.copyTarget = $(`[data-os-panel="${selectedOs}"]`, panel).id;
  }

  async function writeClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) { await navigator.clipboard.writeText(text); return; }
    const host = $('#skill-dialog').open ? $('#skill-dialog') : document.body;
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.setAttribute('readonly', '');
    textarea.style.cssText = 'position:fixed;left:-9999px;opacity:0';
    host.appendChild(textarea);
    textarea.focus(); textarea.select();
    const succeeded = document.execCommand('copy');
    textarea.remove();
    if (!succeeded) throw new Error('Copy command was not accepted');
  }

  async function handleCopy(button) {
    const target = document.getElementById(button.dataset.copyTarget);
    if (!target) return;
    const label = $('.copy-label', button);
    const original = label.textContent;
    try {
      await writeClipboard(target.textContent);
      button.classList.add('is-copied');
      label.textContent = '已复制 ✓';
      button.setAttribute('aria-label', '已复制');
      showToast('内容已复制到剪贴板');
      if (copyTimers.has(button)) window.clearTimeout(copyTimers.get(button));
      copyTimers.set(button, window.setTimeout(() => {
        button.classList.remove('is-copied'); label.textContent = original; button.setAttribute('aria-label', original);
      }, 1800));
    } catch (error) { showToast('请选中代码文本后手动复制'); target.focus(); }
  }

  function showToast(message) {
    const toast = $('#toast');
    $('#toast-message').textContent = message;
    toast.hidden = false;
    if (state.toastTimer) window.clearTimeout(state.toastTimer);
    state.toastTimer = window.setTimeout(() => { toast.hidden = true; }, 2200);
  }

  function handleTabKeys(event, selector, dataKey, activate) {
    const activeTab = event.target.closest && event.target.closest(selector);
    if (!activeTab || !['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return false;
    const tabs = $$(selector, activeTab.closest('[role="tablist"]'));
    let nextIndex = tabs.indexOf(activeTab);
    if (event.key === 'ArrowRight') nextIndex = (nextIndex + 1) % tabs.length;
    if (event.key === 'ArrowLeft') nextIndex = (nextIndex - 1 + tabs.length) % tabs.length;
    if (event.key === 'Home') nextIndex = 0;
    if (event.key === 'End') nextIndex = tabs.length - 1;
    event.preventDefault();
    tabs[nextIndex].focus();
    activate(tabs[nextIndex]);
    return true;
  }

  function bindEvents() {
    document.addEventListener('click', (event) => {
      const clearButton = event.target.closest('[data-clear-search]');
      if (clearButton) { clearFilters(); $('#skill-search').focus(); return; }
      const categoryButton = event.target.closest('[data-category-filter]');
      if (categoryButton) {
        state.activeCategory = categoryButton.dataset.categoryFilter;
        renderCategoryFilters(); filterSkills(); return;
      }
      const returnButton = event.target.closest('[data-close-and-filter]');
      if (returnButton) {
        state.activeCategory = returnButton.dataset.closeAndFilter;
        renderCategoryFilters(); filterSkills(); closeSkill();
        window.requestAnimationFrame(() => $('#skills').scrollIntoView({ behavior: 'smooth' }));
        return;
      }
      const openButton = event.target.closest('[data-open-skill]');
      if (openButton) { openSkill(openButton.dataset.openSkill, { focusGenerator: openButton.dataset.focusGenerator === 'true' }); return; }
      const stageButton = event.target.closest('[data-stage-select]');
      if (stageButton) { selectStage(stageButton.dataset.stageSelect); return; }
      const workflowButton = event.target.closest('[data-workflow]');
      if (workflowButton) { selectWorkflow(workflowButton.dataset.workflow); return; }
      const osTab = event.target.closest('[data-os-tab]');
      if (osTab) { switchOs(osTab); return; }
      const copy = event.target.closest('[data-copy-target]');
      if (copy) handleCopy(copy);
    });

    document.addEventListener('input', (event) => {
      const form = event.target.closest('[data-prompt-skill]');
      if (form) updatePrompt(form);
    });
    document.addEventListener('change', (event) => {
      const form = event.target.closest('[data-prompt-skill]');
      if (!form) return;
      const group = event.target.closest('[data-field-type="checkboxes"]');
      if (group && event.target.matches('input[type="checkbox"]')) {
        const checked = $$('input[type="checkbox"]:checked', group);
        const max = Number(group.dataset.max);
        const min = Number(group.dataset.min);
        if (checked.length > max) { event.target.checked = false; showToast(`每次最多选择 ${max} 项`); }
        else if (checked.length < min) { event.target.checked = true; showToast(`请至少保留 ${min} 项`); }
      }
      updatePrompt(form);
    });
    document.addEventListener('keydown', (event) => {
      if (handleTabKeys(event, '[data-os-tab]', 'osTab', switchOs)) return;
      if (handleTabKeys(event, '[data-workflow]', 'workflow', selectWorkflow)) return;
      const isTyping = ['INPUT', 'TEXTAREA', 'SELECT'].includes(event.target.tagName) || event.target.isContentEditable;
      if ((event.ctrlKey || event.metaKey) && event.key.toLocaleLowerCase() === 'k') {
        event.preventDefault();
        if ($('#skill-dialog').open) closeSkill();
        $('#skill-search').focus(); $('#skill-search').select();
      } else if (event.key === '/' && !isTyping && !$('#skill-dialog').open) {
        event.preventDefault(); $('#skill-search').focus();
      } else if (event.key === 'Escape' && document.activeElement === $('#skill-search') && $('#skill-search').value) {
        $('#skill-search').value = ''; filterSkills();
      }
    });

    $('#skill-search').addEventListener('input', filterSkills);
    $('#clear-search').addEventListener('click', () => { clearFilters(); $('#skill-search').focus(); });
    $('#dialog-close').addEventListener('click', closeSkill);
    $('#skill-dialog').addEventListener('click', (event) => {
      if (event.target !== event.currentTarget) return;
      const dialog = event.currentTarget;
      const rect = dialog.getBoundingClientRect();
      if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) closeSkill();
    });
    $('#skill-dialog').addEventListener('close', () => {
      document.body.classList.remove('modal-open');
      state.currentSkill = null;
      if (state.suppressHashSync) state.suppressHashSync = false; else clearSkillHash();
      if (state.lastFocused && document.contains(state.lastFocused)) state.lastFocused.focus({ preventScroll: true });
      state.lastFocused = null;
    });
    window.addEventListener('hashchange', handleHash);
  }

  function init() {
    initTheme(); renderHeroStats(); renderPipeline(); renderScenarios(); renderCategoryFilters(); renderSkills();
    renderInstall(); renderFaqs(); filterSkills(); bindEvents(); handleHash();
  }

  window.SkillsApp = Object.freeze({ renderPromptTemplate, defaultPromptValues, sourceUrl });
  if (typeof document !== 'undefined') init();
}());
