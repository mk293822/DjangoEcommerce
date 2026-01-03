document.addEventListener("DOMContentLoaded", () => {
  const department = document.getElementById("id_department");
  const category = document.getElementById("id_category");

  if (!department || !category) return;

  department.addEventListener("change", async () => {
    const departmentId = department.value;

    category.innerHTML = '<option value="">---------</option>';

    if (!departmentId) return;

    try {
      const response = await fetch(
        `/admin/products/product/load-categories/?department_id=${departmentId}`
      );
      const data = await response.json();

      data.forEach((cat) => {
        const option = document.createElement("option");
        option.value = cat.id;
        option.textContent = cat.name;
        category.appendChild(option);
      });
    } catch (err) {
      console.error("Category load failed", err);
    }
  });
});
