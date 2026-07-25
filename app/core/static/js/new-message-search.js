document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.querySelector("#new-message-search");
    const userList = document.querySelector("#new-message-user-list");
    const noResultsHint = document.querySelector("#new-message-no-results");

    if (!searchInput || !userList) {
        return;
    }

    const userItems = Array.from(
        userList.querySelectorAll(".new-message-user-item")
    );

    searchInput.addEventListener("input", () => {
        const query = searchInput.value.trim().toLowerCase();
        let visibleCount = 0;

        userItems.forEach((item) => {
            const matches = item.textContent.toLowerCase().includes(query);
            item.style.display = matches ? "" : "none";

            if (matches) {
                visibleCount += 1;
            }
        });

        if (noResultsHint) {
            noResultsHint.style.display = visibleCount === 0 ? "" : "none";
        }
    });
});
