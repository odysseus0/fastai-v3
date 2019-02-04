var el = x => document.getElementById(x);

const showPicker = (inputId) => { el('file-input').click(); }

const showPicked = (input) => {
    el('upload-label').innerHTML = input.files[0].name;
    var reader = new FileReader();
    reader.onload = (e) => {
        el('image-picked').src = e.target.result;
        el('image-picked').className = '';
    }
    reader.readAsDataURL(input.files[0]);
}

const analyze = () => {
    var uploadFiles = el('file-input').files;
    if (uploadFiles.length != 1) alert('Please select 1 file to analyze!');

    el('analyze-button').innerHTML = 'Analyzing...';
    var xhr = new XMLHttpRequest();
    var loc = window.location
    const serverURL = `${loc.protocol}//${loc.hostname}:${loc.port}`
    xhr.open('POST', `${serverURL}/analyze`, true);
    xhr.onerror = () => {alert (xhr.responseText);}
    xhr.onload = (e) => {
        if (xhr.readyState === 4) {
            var response = JSON.parse(e.target.responseText);
            el('result-image').src = serverURL + '/' + response['resultURL'];
            el('result-image').className = '';
        }
        el('analyze-button').innerHTML = 'Analyze';
    }

    var fileData = new FormData();
    fileData.append('file', uploadFiles[0]);
    xhr.send(fileData);
}

