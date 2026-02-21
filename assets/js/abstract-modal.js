document.addEventListener('DOMContentLoaded', () => {
  const backdrop = document.getElementById('abstract-backdrop');
  const modal = document.getElementById('abstract-modal');
  const closeButton = document.getElementById('abstract-modal-close');
  const titleNode = document.getElementById('abstract-title');
  const bodyNode = document.getElementById('abstract-body');
  const linkNode = document.getElementById('abstract-ssrn-link');

  if (!backdrop || !modal || !closeButton || !titleNode || !bodyNode || !linkNode) {
    return;
  }

  let activeTrigger = null;

  const openModal = (trigger) => {
    activeTrigger = trigger;
    titleNode.textContent = trigger.dataset.title || 'Working Paper';
    bodyNode.textContent = trigger.dataset.abstract || 'Abstract unavailable. Please see SSRN page.';
    linkNode.href = trigger.dataset.url || '#';

    backdrop.hidden = false;
    modal.hidden = false;
    backdrop.setAttribute('aria-hidden', 'false');
    document.body.classList.add('modal-open');
    closeButton.focus();
  };

  const closeModal = () => {
    backdrop.hidden = true;
    modal.hidden = true;
    backdrop.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('modal-open');

    if (activeTrigger) {
      activeTrigger.focus();
      activeTrigger = null;
    }
  };

  document.addEventListener('click', (event) => {
    const trigger = event.target.closest('.js-view-abstract');
    if (!trigger) return;

    event.preventDefault();
    openModal(trigger);
  });

  closeButton.addEventListener('click', closeModal);
  backdrop.addEventListener('click', closeModal);
  modal.addEventListener('click', (event) => {
    event.stopPropagation();
  });

  document.addEventListener('keydown', (event) => {
    if (modal.hidden) return;
    if (event.key === 'Escape') {
      event.preventDefault();
      closeModal();
    }
  });
});
