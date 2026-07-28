document.addEventListener("mouseover", function (event) {

    const entity = event.target.closest(".entity");

    if (!entity) return;

    const type = entity.dataset.type;

    // Default entities do not link/highlight
    if (type === "default") {
        return;
    }

    const name = entity.dataset.entity;

    document.querySelectorAll(".entity").forEach(other => {

        if (
            other.dataset.entity === name &&
            other.dataset.type !== "default"
        ) {
            other.classList.add("entity-highlight");
        }

    });

});

document.addEventListener("mouseout", function (event) {

    const entity = event.target.closest(".entity");

    if (!entity) return;

    document.querySelectorAll(".entity").forEach(other => {
        other.classList.remove("entity-highlight");
    });

});
