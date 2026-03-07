document.addEventListener("DOMContentLoaded", function () {
  console.log("Feedback form loaded");

  var forms = document.querySelectorAll("form");
  forms.forEach(function (form) {
    form.addEventListener("submit", function () {
      var submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = "Submitting...";
      }
    });
  });
});

function togglePassword() {
  var password = document.getElementById("password");
  var icon = document.querySelector(".toggle-password");

  if (!password) {
    return;
  }

  if (password.type === "password") {
    password.type = "text";
    if (icon) {
      icon.classList.remove("fa-eye");
      icon.classList.add("fa-eye-slash");
    }
  } else {
    password.type = "password";
    if (icon) {
      icon.classList.remove("fa-eye-slash");
      icon.classList.add("fa-eye");
    }
  }
}
