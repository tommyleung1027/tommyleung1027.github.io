document.addEventListener('DOMContentLoaded', () => {
  const triggers = Array.from(document.querySelectorAll('.js-view-abstract'));
  const overlay = document.getElementById('abstract-modal-overlay');
  const modal = document.getElementById('abstract-modal');
  const closeButton = document.getElementById('abstract-modal-close');
  const titleNode = document.getElementById('abstract-modal-title');
  const bodyNode = document.getElementById('abstract-modal-body');
  const linkNode = document.getElementById('abstract-modal-link');

  if (!triggers.length || !overlay || !modal || !closeButton || !titleNode || !bodyNode || !linkNode) {
    return;
  }

  const focusableSelector = [
    'a[href]',
    'button:not([disabled])',
    'textarea:not([disabled])',
    'input:not([disabled])',
    'select:not([disabled])',
    '[tabindex]:not([tabindex="-1"])'
  ].join(',');

  let activeTrigger = null;

  const setOpenState = (isOpen) => {
    overlay.hidden = !isOpen;
    overlay.setAttribute('aria-hidden', String(!isOpen));
    document.body.classList.toggle('modal-open', isOpen);
  };

  const closeModal = () => {
    setOpenState(false);
    document.removeEventListener('keydown', onKeyDown);

    if (activeTrigger) {
      activeTrigger.focus();
    }
  };

  const trapTab = (event) => {
    if (event.key !== 'Tab') return;

    const focusable = Array.from(modal.querySelectorAll(focusableSelector));
    if (!focusable.length) {
      event.preventDefault();
      return;
    }

    const first = focusable[0];
    const last = focusable[focusable.length - 1];

    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  };

  const onKeyDown = (event) => {
    if (event.key === 'Escape') {
      event.preventDefault();
      closeModal();
      return;
    }
    trapTab(event);
  };

  const openModal = (trigger) => {
    activeTrigger = trigger;

    titleNode.textContent = trigger.dataset.title || 'Working Paper';
    bodyNode.textContent = trigger.dataset.abstract || 'Abstract unavailable. Please see SSRN page.';
    linkNode.href = trigger.dataset.url || '#';

    setOpenState(true);
    document.addEventListener('keydown', onKeyDown);
    closeButton.focus();
  };

  triggers.forEach((trigger) => {
    trigger.addEventListener('click', () => openModal(trigger));
  });

  closeButton.addEventListener('click', closeModal);
  overlay.addEventListener('click', (event) => {
    if (event.target === overlay) {
      closeModal();
    }
  });
});
