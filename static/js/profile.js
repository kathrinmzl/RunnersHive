 const deleteModal = document.getElementById('deleteModal');
  const modalTitle = document.getElementById('modalEventTitle');
  const deleteForm = document.getElementById('deleteForm');

  deleteModal.addEventListener('show.bs.modal', event => {
    const button = event.relatedTarget;
    const title = button.getAttribute('data-event-title');
    const url = button.getAttribute('data-delete-url');

    modalTitle.textContent = title;
    deleteForm.action = url;
  });