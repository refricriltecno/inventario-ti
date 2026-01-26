function addField(containerId, inputName) {
    const container = document.getElementById(containerId);
    const div = document.createElement('div');
    div.className = 'input-group mb-2';
    
    div.innerHTML = `
        <input type="text" name="${inputName}" class="form-control" placeholder="Novo item...">
        <button type="button" class="btn btn-outline-danger" onclick="removeField(this)">X</button>
    `;
    
    container.appendChild(div);
}

function removeField(btn) {
    btn.parentElement.remove();
}