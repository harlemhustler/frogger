const form = document.getElementById("job-form");
const paths = { source: "", destination: "" };
const run = document.getElementById("run");
const status = document.getElementById("status");
const progress = document.getElementById("progress");
const report = document.getElementById("report");

const terminal = new Set(["completed", "completed_with_errors", "failed"]);
const labels = {
  queued: "Queued", sorting: "Sorting", background_removal: "Removing backgrounds",
  completed: "Completed", completed_with_errors: "Completed with errors", failed: "Failed",
};

async function request(path, options) {
  const response = await fetch("/api" + path, options);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(typeof data.detail === "string" ? data.detail : "Request failed (" + response.status + ").");
  }
  return data;
}

const sourceButton = document.getElementById("folder-browse");
const destinationButton = document.getElementById("destination-browse");

function attachFolderPicker(kind, button, outputId) {
  button.addEventListener("click", async () => {
    sourceButton.disabled = destinationButton.disabled = run.disabled = true;
    try {
      const result = await request("/folder-picker", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ kind, current: paths[kind] }),
      });
      if (result.path) {
        paths[kind] = result.path;
        document.getElementById(outputId).textContent = result.path;
      }
    } catch (error) {
      status.textContent = error.message;
    } finally {
      sourceButton.disabled = destinationButton.disabled = run.disabled = false;
      button.focus();
    }
  });
}

attachFolderPicker("source", sourceButton, "folder-path");
attachFolderPicker("destination", destinationButton, "destination-path");
function show(job) {
  progress.value = job.progress;
  status.textContent = (labels[job.status] || labels[job.phase] || job.phase) + " — " + job.progress + "%";
  const { bot_id, job_id, status: state, phase, progress: percent } = job;
  window.dispatchEvent(new CustomEvent("gorgon:bot-event", {
    detail: { bot_id, job_id, status: state, phase, progress: percent },
  }));
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (run.disabled) return;
  if (!paths.source || !paths.destination) {
    status.textContent = 'Choose both a source and a destination folder.';
    return;
  }
  const operations = new FormData(form).getAll("operations");
  if (!operations.length) {
    status.textContent = "Select at least one operation.";
    return;
  }
  sourceButton.disabled = destinationButton.disabled = run.disabled = true;
  progress.value = 0;
  report.textContent = "";
  status.textContent = "Submitting…";
  try {
    let job = await request("/jobs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ folder: paths.source, destination: paths.destination, operations }),
    });
    show(job);
    while (!terminal.has(job.status)) {
      await new Promise(resolve => setTimeout(resolve, 750));
      job = await request("/jobs/" + encodeURIComponent(job.job_id));
      show(job);
    }
    report.textContent = JSON.stringify(job.result || { error: job.error }, null, 2);
  } catch (error) {
    status.textContent = error.message;
  } finally {
    sourceButton.disabled = destinationButton.disabled = run.disabled = false;
  }
});
