document.addEventListener('DOMContentLoaded', function() {
    console.log("House Hunt App Loaded!");

    // Example of adding a click event to a button
    let addButton = document.querySelector('.btn-success');
    if (addButton) {
        addButton.addEventListener('click', function() {
            alert('Adding a new house!');
        });
    }
});
