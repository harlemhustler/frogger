(() => {
  for (const scene of document.querySelectorAll('[data-scene="frogger"]')) {
    const panels = [...scene.querySelectorAll('.gorgon-frogger')];
    const newStep = () => ({operation: '', source: null, destination: null, preview: null, slide: 0});
    const steps = [newStep()];
    let active = 0;
    let message = '';
    const sourceFor = index => index === 0 ? steps[0].source : steps[index - 1].destination;
    const operations = {sort: 'Sort', background_removal: 'Background remove'};
    const find = (panel, selector) => panel.querySelector(selector);

    function render() {
      const step = steps[active];
      const folders = {source: sourceFor(active), destination: step.destination};
      for (const panel of panels) {
        for (const tab of panel.querySelectorAll('[data-frogger-step]')) {
          const index = Number(tab.dataset.froggerStep);
          tab.disabled = index >= steps.length;
          tab.setAttribute('aria-pressed', String(index === active));
          tab.textContent = (index + 1) + '. ' + (operations[steps[index]?.operation] || 'Operation');
        }
        find(panel, '[data-frogger-operation]').value = step.operation;
        find(panel, '[data-frogger-folder="source"]').hidden = active > 0;
        for (const view of panel.querySelectorAll('[data-frogger-view]')) {
          const key = view.dataset.froggerView;
          const folder = folders[key];
          view.hidden = !folder;
          view.textContent = folder ? folder.name + (key === 'source' && active > 0 ? ' (locked)' : '') : '';
          view.setAttribute('aria-label', (key === 'source' ? 'Source' : 'Destination') + ' folder: ' + (folder?.name || '') +
            (key === 'source' && active > 0 ? ', locked to the preceding destination' : ''));
          view.setAttribute('aria-pressed', String(step.preview === key && !!folder));
        }
        find(panel, '[data-frogger-chain]').hidden =
          active !== steps.length - 1 || steps.length === 4 || !step.operation || !step.destination;
        const folder = folders[step.preview];
        find(panel, '[data-frogger-folder-title]').textContent = folder?.name || 'Folder contents';
        find(panel, '[data-frogger-folder-status]').textContent = message ||
          (folder ? (folder.entries.length ? '' : 'This folder is empty.') : 'Click a selected source or destination folder to view its contents.');
        const entries = folder?.entries || [];
        const at = Math.min(step.slide, Math.max(0, entries.length - 1));
        const entry = entries[at];
        const slide = find(panel, '[data-frogger-slide]');
        slide.textContent = entry ? entry.name + (entry.directory ? '/' : '') : '';
        slide.classList.toggle('is-empty', !entry);
        find(panel, '[data-frogger-position]').textContent = entries.length ? (at + 1) + ' / ' + entries.length : '0 / 0';
        find(panel, '[data-frogger-slide-by="-1"]').disabled = at === 0;
        find(panel, '[data-frogger-slide-by="1"]').disabled = at + 1 >= entries.length;
      }
    }

    function setFolder(index, key, name, entries) {
      steps[index][key] = {
        name,
        entries: entries.sort((a, b) => Number(b.directory) - Number(a.directory) || a.name.localeCompare(b.name))
      };
      steps[index].preview = null;
      steps[index].slide = 0;
      message = '';
      render();
    }

    for (const panel of panels) {
      let pending;
      const picker = find(panel, '[data-frogger-picker]');
      picker.addEventListener('change', () => {
        const files = [...picker.files];
        if (!pending || !files.length) return;
        const entries = new Map();
        const name = files[0].webkitRelativePath.split('/')[0];
        for (const file of files) {
          const [, first, ...nested] = file.webkitRelativePath.split('/');
          if (first) entries.set(first, {name: first, directory: nested.length > 0});
        }
        setFolder(pending.index, pending.key, name, [...entries.values()]);
        pending = null;
      });

      panel.addEventListener('click', async event => {
        const button = event.target.closest('button');
        if (!button || button.disabled) return;
        message = '';
        if (button.hasAttribute('data-frogger-step')) {
          active = Number(button.dataset.froggerStep);
        } else if (button.hasAttribute('data-frogger-chain')) {
          if (active !== steps.length - 1 || steps.length >= 4 || !steps[active].operation || !steps[active].destination) return;
          active = steps.push(newStep()) - 1;
          render();
          find(panel, '[data-frogger-operation]').focus();
          return;
        } else if (button.hasAttribute('data-frogger-view')) {
          steps[active].preview = button.dataset.froggerView;
          steps[active].slide = 0;
        } else if (button.hasAttribute('data-frogger-slide-by')) {
          steps[active].slide += Number(button.dataset.froggerSlideBy);
        } else if (button.hasAttribute('data-frogger-folder')) {
          const index = active;
          const key = button.dataset.froggerFolder;
          if (key === 'source' && index > 0) return;
          if (typeof window.showDirectoryPicker === 'function' && window.top === window.self) {
            try {
              const handle = await window.showDirectoryPicker({mode: 'read'});
              const entries = [];
              for await (const entry of handle.values()) entries.push({name: entry.name, directory: entry.kind === 'directory'});
              setFolder(index, key, handle.name, entries);
              return;
            } catch (error) {
              if (error.name === 'AbortError') return;
              if (error.name !== 'SecurityError') {
                message = 'Could not read that folder. Choose another folder.';
                render();
                return;
              }
            }
          }
          pending = {index, key};
          picker.value = '';
          picker.click();
          return;
        }
        render();
      });

      find(panel, '[data-frogger-operation]').addEventListener('change', event => {
        steps[active].operation = event.target.value;
        message = '';
        render();
      });
    }
    render();
  }
})();
