function createInputField(id, value) {
  let input = document.createElement('input');
  input.id = id;
  input.value = value;
  input.className = 'form-control';
  input.required = true;
  return input;
}

function createFormGroup(property, value) {
  let formGroup = document.createElement('div');
  formGroup.className = 'form-group mb-3';

  let label = document.createElement('label');
  label.textContent = property.charAt(0).toUpperCase() + property.slice(1) + ':';
  label.for = property;
  label.className = 'form-label';

  let input = createInputField(property, value);

  formGroup.appendChild(label);
  formGroup.appendChild(input);

  return formGroup;
}

function createListGroup(property, values) {
  let listGroup = document.createElement('ul');
  listGroup.className = 'list-group mb-3';

  values.forEach((value, i) => {
    let listItem = document.createElement('li');
    listItem.className = 'list-group-item';

    let input = createInputField(property + i, value);

    listItem.appendChild(input);
    listGroup.appendChild(listItem);
  });

  return listGroup;
}

function uploadRecipe() {
  let form = document.createElement('form');
  form.id = 'uploadRecipe';
  form.className = 'mb-3';

  for (let property in uploadedRecipe) {
    let element;
    if (property === 'ingredients' || property === 'directions') {
      element = createListGroup(property, uploadedRecipe[property]);
    } else {
      element = createFormGroup(property, uploadedRecipe[property]);
    }
    form.appendChild(element);
  }

  let submitButton = document.createElement('button');
  submitButton.type = 'submit';
  submitButton.textContent = 'Submit';
  submitButton.className = 'btn btn-primary mt-3';

  form.appendChild(submitButton);

  form.addEventListener('submit', function(event) {
    event.preventDefault();

    for (let property in uploadedRecipe) {
      if (property === 'ingredients' || property === 'directions') {
        for (let i = 0; i < uploadedRecipe[property].length; i++) {
          uploadedRecipe[property][i] = document.getElementById(property + i).value;
        }
      } else {
        uploadedRecipe[property] = document.getElementById(property).value;
      }
    }

    submitRecipe(uploadedRecipe);
  });

  document.getElementById('recipeContent').appendChild(form);
}