(() => {
  for (const scene of document.querySelectorAll('[data-scene="frogger"]')) {
    const panels = [...scene.querySelectorAll('.gorgon-frogger')];
    const newStep = () => ({operation: '', source: null, destination: null, preview: null, slide: 0, variants: [''], criteriaReady: false});
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
        find(panel,'[data-frogger-criteria]').hidden = step.operation !== 'sort';
        const variants = find(panel,'[data-frogger-variants]');
        if (variants.children.length !== step.variants.length) {
          variants.replaceChildren(...step.variants.map((value,index) => {
            const label = document.createElement('label');
            label.textContent = 'Variant ' + (index + 1);
            const input = document.createElement('input');
            input.dataset.froggerVariant = index;
            input.setAttribute('aria-label','Variant ' + (index + 1) + ' handle');
            input.placeholder = index ? 'Olive Green' : 'Navy Blue';
            input.maxLength = 80;
            label.append(input);
            return label;
          }));
        }
        for (const input of variants.querySelectorAll('input')) {
          input.value = step.variants[Number(input.dataset.froggerVariant)];
          input.disabled = running;
        }
        find(panel,'[data-frogger-add-variant]').disabled = running || step.variants.length >= 30;
        find(panel,'[data-frogger-proceed]').disabled = running;
        find(panel,'[data-frogger-criteria-status]').textContent = step.criteriaReady ? 'Ready: ' + step.variants.map(v=>v.trim()).join(', ') : 'Enter each color handle, then proceed.';
        find(panel,'[data-frogger-run]').disabled = running || !connected || !step.criteriaReady || step.operation !== 'sort';
        find(panel,'[data-frogger-run]').textContent = running ? 'Sorting...' : 'Run Sort';
        find(panel,'[data-frogger-download]').hidden = !artifact;
        for (const control of panel.querySelectorAll('[data-frogger-folder], [data-frogger-chain], [data-frogger-step], [data-frogger-operation]')) {
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
          // Sort variants are entered explicitly; folder names never overwrite them.
        }
        pending = null;
      });

      panel.addEventListener('click', async event => {
        const button = event.target.closest('button');
        if (!button || button.disabled) return;
        message = '';
        if (button.hasAttribute('data-frogger-add-variant')) {
          if (!steps[active].variants.at(-1).trim()) { message = 'Enter a handle before adding another.'; render(); return; }
          steps[active].variants.push('');
          steps[active].criteriaReady = false;
          artifact = null;
          render();
          find(panel,'[data-frogger-variants]').lastElementChild.querySelector('input').focus();
          return;
        } else if (button.hasAttribute('data-frogger-proceed')) {
          const names = steps[active].variants.map(value=>value.trim());
          if (names.some(name=>!name || name.length>80 || /[\\/:*?"<>|\x00-\x1f]/.test(name) || name.startsWith('.') || ['unsorted','no bg'].includes(name.toLowerCase()))) {
            message = 'Enter a valid folder handle for every variant.';
          } else if (new Set(names.map(name=>name.toLowerCase())).size !== names.length) {
            message = 'Each variant handle must be different.';
          } else {
            steps[active].variants = names;
            steps[active].criteriaReady = true;
            message = connected ? 'Criteria ready. Choose your source and run Sort.' : 'Criteria ready. Use Quick Actions Start to connect.';
          }
          render();
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
            const folders = steps[0].variants.map(name=>name.trim());
            if (!steps[0].criteriaReady) throw new Error('Confirm your variant handles with Proceed.');
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
                // Keep explicit variant handles unchanged.
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

      panel.addEventListener('input',event=>{
        if (!event.target.hasAttribute('data-frogger-variant')) return;
        steps[active].variants[Number(event.target.dataset.froggerVariant)] = event.target.value;
        steps[active].criteriaReady = false;
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
    scene.addEventListener('gorgon-command',async event=>{
      const action = event.detail.command;
      if (running) { event.detail.report('Wait for the current Frogger request to finish.'); return; }
      if (action === 'Stop') {
        connection?.dispose(); connection = null; connected = false;
        message = 'Frogger disconnected. Completed downloads are preserved.';
        event.detail.report(message); render(); return;
      }
      running = true;
      try {
        if (action === 'Restart') { connection?.dispose(); connection = null; connected = false; }
        connection ||= window.GorgonConnections.create('frogger');
        const request = connected ? connection.request('health') : connection.connect();
        message = 'Checking Frogger backend; complete sign-in if prompted.'; render();
        await request; connected = true;
        message = action === 'Diagnose' ? 'Gorgon connection healthy. Frogger supports Sort: 20 images / 8 MiB.' : 'Frogger connected. Configure variants and run Sort.';
      } catch(error) { connected = false; message = error.message; }
      finally { running = false; event.detail.report(message); render(); }
    });
    render();
  }
})();
