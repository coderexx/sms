$(document).ready(function () {
    $('.dataTable').DataTable({
        paging: false,     // ❌ Disable pagination
        searching: false,  // ❌ Disable search
        info: false,
    });
});


  document.addEventListener("DOMContentLoaded", () => {
    const counters = document.querySelectorAll(".counter");

    counters.forEach(counter => {
      const updateCount = () => {
        const target = +counter.getAttribute("data-target");
        const count = +counter.innerText;
        const increment = target / 50;

        if (count < target) {
          counter.innerText = Math.ceil(count + increment);
          setTimeout(updateCount, 50);
        } else {
          counter.innerText = target;
        }
      };
      updateCount();
    });
  });