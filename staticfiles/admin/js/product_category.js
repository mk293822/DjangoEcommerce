(function ($) {
  $(document).ready(function () {
    const department = $("#id_department");
    const category = $("#id_category");

    if (!department.length || !category.length) return;

    department.on("change", function () {
      const departmentId = $(this).val();

      category.empty();
      category.append('<option value="">---------</option>');

      if (!departmentId) return;

      fetch(`load-categories/?department_id=${departmentId}`)
        .then((response) => response.json())
        .then((data) => {
          data.forEach((cat) => {
            category.append(`<option value="${cat.id}">${cat.name}</option>`);
          });
        })
        .catch((err) => console.error(err));
    });
  });
})(django.jQuery);
