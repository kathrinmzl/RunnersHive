 const deleteModal = document.getElementById('deleteModal');
  const modalTitle = document.getElementById('modalEventTitle');
  const modalDate = document.getElementById('modalEventDate');
  const deleteForm = document.getElementById('deleteForm');

  deleteModal.addEventListener('show.bs.modal', event => {
    const button = event.relatedTarget;
    const title = button.getAttribute('data-event-title');
    const date = button.getAttribute('data-event-date');
    const url = button.getAttribute('data-delete-url');

    modalTitle.textContent = title;
    modalDate.textContent = date;
    deleteForm.action = url;
  });