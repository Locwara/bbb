document.addEventListener("DOMContentLoaded", function () {
    const passwordinput = document.getElementById("password");
    const showpassword = document.getElementById("showpassword");

    showpassword.addEventListener("change", function () {
        if (this.checked) {
            passwordinput.type = 'text';

        } else {
            passwordinput.type = "password";
        }
    });
});