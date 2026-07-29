document.addEventListener("mouseover", function (event) {

    const entity = event.target.closest(".entity");

    if (!entity) return;

    const type = entity.dataset.type;

    // Default entities do not highlight
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


//
// Track currently open popup entity
//

let activeEntity = null;



//
// Click entity -> show/hide definition popup
//

document.addEventListener("click", function (event) {

    const entity = event.target.closest(".entity");
    const popup = event.target.closest(".entity-popup");


    // Clicking inside popup does nothing
    if (popup) {
        return;
    }


    // Clicking an entity
    if (entity) {

        const description = entity.dataset.description;


        // No definition
        if (!description) {
            closeDefinitionPopup();
            return;
        }


        // Clicking the same variable closes it
        if (activeEntity === entity) {
            closeDefinitionPopup();
            return;
        }


        // Clicking a different variable opens/repositions it
        showDefinitionPopup(entity);

        return;
    }


    // Clicking elsewhere closes popup
    closeDefinitionPopup();

});



//
// Create popup
//

function showDefinitionPopup(entity) {

    closeDefinitionPopup();


    activeEntity = entity;


    const popup = document.createElement("div");

    popup.className = "entity-popup";


    popup.innerHTML = `
        <div class="entity-popup-title">
            ${entity.dataset.entity}
        </div>

        <div class="entity-popup-meta">
            ${entity.dataset.type} | ${entity.dataset.scope}
        </div>

        <div class="entity-popup-description">
            ${entity.dataset.description}
        </div>
    `;


    document.body.appendChild(popup);


    const rect = entity.getBoundingClientRect();

    popup.style.left =
        `${rect.left + window.scrollX}px`;

    popup.style.top =
        `${rect.bottom + window.scrollY + 8}px`;

}



//
// Remove popup
//

function closeDefinitionPopup() {

    const existing = document.querySelector(
        ".entity-popup"
    );


    if (existing) {
        existing.remove();
    }


    activeEntity = null;

}
