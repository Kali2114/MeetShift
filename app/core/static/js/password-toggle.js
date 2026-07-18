document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".password-toggle").forEach((button) => {
        button.addEventListener("click", () => {
            const input = document.getElementById(
                button.dataset.passwordTarget
            );

            if (!input) {
                return;
            }

            const passwordIsHidden = input.type === "password";

            input.type = passwordIsHidden ? "text" : "password";
            button.textContent = passwordIsHidden ? "🙈" : "👁";

            button.setAttribute(
                "aria-label",
                passwordIsHidden ? "Hide password" : "Show password"
            );

            button.setAttribute(
                "title",
                passwordIsHidden ? "Hide password" : "Show password"
            );
        });
    });
});
