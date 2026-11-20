(() => {
  for (const scene of document.querySelectorAll('[data-scene="frogger"]')) {
    const panels = [...scene.querySelectorAll('.gorgon-frogger')];
    const newStep = () => ({operation: '', source: null, destination: null, preview: null, slide: 0});
    const steps = [newStep()];
    let active = 0;
    let message = '';
    let connection;
    let connected = false;
    let running = false;
    let artifact = null;
    const sourceFor = index => index === 0 ? steps[0].source : steps[index - 1].destination;
    const operations = {sort: 'Sort', background_removal: 'Background remove'};
    const find = (panel, selector) => panel.querySelector(selector);

    function render() {
      const step = steps[active];
      const folders = {source: sourceFor(active), destination: step.destination};
      for (const panel of panels) {
        find(panel,'[data-frogger-connect]').disabled = running;
        find(panel,'[data-frogger-connect]').textContent = connected ? 'Reconnect Gorgon' : 'Connect to Gorgon';
        find(panel,'[data-frogger-run]').disabled = running || !connected;
        find(panel,'[data-frogger-run]').textContent = running ? 'Sorting...' : 'Run Sort';
        find(panel,'[data-frogger-download]').hidden = !artifact;
        for (const control of panel.querySelectorAll('[data-frogger-folder], [data-frogger-chain], [data-frogger-step], [data-frogger-operation], [data-frogger-colors]')) {
          control.disabled = running;
        }
        for (const tab of panel.querySelectorAll('[data-frogger-step]')) {
          const index = Number(tab.dataset.froggerStep);
          tab.disabled = running || index >= steps.length;
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

    function setFolder(index, key, name, entries, files = []) {
      artifact = null;
      steps[index][key] = {
        name, files,
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
        setFolder(pending.index, pending.key, name, [...entries.values()],
          files.filter(file => file.webkitRelativePath.split('/').length === 2));
        if (pending.key === 'destination') {
          for (const target of panels) find(target,'[data-frogger-colors]').value = [...entries.values()].filter(entry=>entry.directory).map(entry=>entry.name).join(', ');
        }
        pending = null;
      });

      panel.addEventListener('click', async event => {
        const button = event.target.closest('button');
        if (!button || button.disabled) return;
        message = '';
        if (button.hasAttribute('data-frogger-connect')) {
          try {
            connection ||= window.GorgonConnections.create('frogger');
            running = true;
            message = 'Complete Gorgon sign-in in the connection tab.';
            const connecting = connection.connect();
            render();
            await connecting;
            connected = true;
            message = 'Connected to Gorgon.';
          } catch (error) { message = error.message; connected = false; }
          finally { running = false; render(); }
          return;
        } else if (button.hasAttribute('data-frogger-download')) {
          const bytes = Uint8Array.from(atob(artifact.archive), char => char.charCodeAt(0));
          const url = URL.createObjectURL(new Blob([bytes],{type:'application/zip'}));
          const link = document.createElement('a');
          link.href = url;
          link.download = 'frogger-' + artifact.jobId + '.zip';
          link.click();
          setTimeout(()=>URL.revokeObjectURL(url),10000);
          return;
        } else if (button.hasAttribute('data-frogger-run')) {
          try {
            if (steps.length !== 1 || steps[0].operation !== 'sort') throw new Error('Choose Sort as a single operation for this hosted release.');
            const source = sourceFor(0);
            const files = (source?.files || []).filter(file=>/\.(png|jpe?g|webp)$/i.test(file.name));
            if (!files.length || files.length > 20 || files.reduce((sum,file)=>sum+file.size,0)>8*1024*1024) {
              throw new Error('Choose 1 to 20 source images totaling at most 8 MiB.');
            }
            const folders = find(panel,'[data-frogger-colors]').value.split(',').map(name=>name.trim()).filter(Boolean);
            if (!folders.length) throw new Error('Select destination color folders or enter their names.');
            running = true;
            artifact = null;
            message = 'Uploading and sorting images...';
            render();
            const uploads = [];
            for (const file of files) {
              const encoded = await new Promise((resolve,reject)=>{
                const reader = new FileReader();
                reader.onload=()=>resolve(String(reader.result).split(',')[1]);
                reader.onerror=()=>reject(new Error('Could not read source image.'));
                reader.readAsDataURL(file);
              });
              uploads.push({name:file.name,data:encoded});
            }
            artifact = await connection.request('run',{operation:'sort',folders,files:uploads});
            message = 'Completed: ' + artifact.sorted + ' sorted, ' + artifact.unsorted + ' unmatched. Download your ZIP.';
          } catch (error) { message = error.message; }
          finally { running = false; render(); }
          return;
        } else if (button.hasAttribute('data-frogger-step')) {
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
              const files = [];
              for await (const entry of handle.values()) {
                entries.push({name:entry.name,directory:entry.kind === 'directory'});
                if (key === 'source' && entry.kind === 'file') files.push(await entry.getFile());
              }
              setFolder(index, key, handle.name, entries, files);
              if (key === 'destination') {
                for (const target of panels) find(target,'[data-frogger-colors]').value = entries.filter(entry=>entry.directory).map(entry=>entry.name).join(', ');
              }
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

      find(panel,'[data-frogger-colors]').addEventListener('input',event=>{
        for (const target of panels) if (target !== panel) find(target,'[data-frogger-colors]').value = event.target.value;
        artifact = null;
        render();
      });
      find(panel, '[data-frogger-operation]').addEventListener('change', event => {
        steps[active].operation = event.target.value;
        artifact = null;
        message = '';
        render();
      });
    }
    render();
  }
})();
