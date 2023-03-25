const input_many = document.getElementById('file-upload');
const input_alone = document.getElementById('cover-file');
const alone = document.getElementById('alone');
const many = document.getElementById('many');
const nb_fichiers = document.getElementById('nb_fichiers');

input_many.addEventListener('change', file_names);
input_alone.addEventListener('change', file_name);

function file_names() {
    many.innerHTML = '';
    nb_fichiers.innerHTML = '';
    const files = input_many.files;
    const item = document.createElement('div');
    item.textContent = files.length;
    nb_fichiers.appendChild(item);

    const elem = document.createElement('div');
    elem.textContent = limitString(input_many.files[0].name);
    many.appendChild(elem);
    if (files.length > 1) {
        const item = document.createElement('div');
        item.textContent = 'et ' + String(files.length - 1) + ' autres';
        many.appendChild(item);
    }
}

function file_name(){
    alone.innerHTML = '';
    const item = document.createElement('div');
    item.textContent = limitString(input_alone.files[0].name);
    alone.appendChild(item);
}

function limitString(str) {
    const maxLength = 20;
    if (str.length > maxLength + 5) {
        return str.substring(0, maxLength) + "•••." + str.split('.')[1];
    } else {
        return str;
    }
}