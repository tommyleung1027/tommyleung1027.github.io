document.addEventListener('DOMContentLoaded', () => {
  const backdrop = document.getElementById('abstract-backdrop');
  const modal = document.getElementById('abstract-modal');
  const closeButton = document.getElementById('abstract-modal-close');
  const titleNode = document.getElementById('abstract-title');
  const bodyNode = document.getElementById('abstract-body');
  const primaryLinkNode = document.getElementById('abstract-primary-link');

  if (!backdrop || !modal || !closeButton || !titleNode || !bodyNode || !primaryLinkNode) {
    return;
  }

  let activeTrigger = null;

  const setLink = (node, href, label) => {
    if (href) {
      node.href = href;
      node.textContent = label;
      node.hidden = false;
    } else {
      node.href = '#';
      node.hidden = true;
    }
  };

  const openModal = (trigger) => {
    activeTrigger = trigger;
    titleNode.textContent = trigger.dataset.title || 'Paper';

    const abstractText = trigger.dataset.abstract || 'Abstract unavailable.';
    bodyNode.textContent = abstractText;

    const primaryHref = trigger.dataset.url || '';
    setLink(primaryLinkNode, primaryHref, 'Open paper link');

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
