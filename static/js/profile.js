// Grab references to DOM elements 
const deleteModal = document.getElementById('deleteModal'); 
const modalTitle = document.getElementById('modalEventTitle'); 
const modalDate = document.getElementById('modalEventDate'); 
const deleteForm = document.getElementById('deleteForm'); 

// Listen for the modal to be shown (Bootstrap's 'show.bs.modal' event)
deleteModal.addEventListener('show.bs.modal', event => {
    // The button that triggered the modal
    const button = event.relatedTarget;

    // Extract event data from button's data-* attributes
    const title = button.getAttribute('data-event-title'); 
    const date = button.getAttribute('data-event-date'); 
    // URL to submit the delete request to  
    const url = button.getAttribute('data-delete-url');    

    // Update modal content with the selected event's information
    modalTitle.textContent = title;
    modalDate.textContent = date;

    // Set the form's action attribute to the delete URL
    // Ensures that request goes to the correct endpoint when deletion gets confirmed
    deleteForm.action = url;
});
