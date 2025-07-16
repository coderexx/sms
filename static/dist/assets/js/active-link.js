// Get current path from URL (without domain)
  const currentPath = window.location.pathname;

  // Get all menu links
  const menuLinks = document.querySelectorAll('.menu-link');

  menuLinks.forEach(link => {
    const href = link.getAttribute('href');

    // Check if current path matches this link's href
    if (href === currentPath) {
      const li = link.closest('.menu-item');
      li.classList.add('active');

      // Also activate parent menu (e.g., the dropdown toggle)
      const parentMenu = li.closest('.menu-sub');
      if (parentMenu) {
        const parentItem = parentMenu.closest('.menu-item');
        parentItem.classList.add('active');
      }
    }
  });