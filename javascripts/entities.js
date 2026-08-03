let activeEntity = null;



//
// Hover highlighting
//

document.addEventListener(
    "mouseover",
    function(event) {

        const entity =
            event.target.closest(".entity");


        if (!entity) return;


        const name =
            entity.dataset.entity;


        document
            .querySelectorAll(".entity")
            .forEach(other => {

                if (
                    other.dataset.entity === name
                ) {
                    other.classList.add(
                        "entity-highlight"
                    );
                }

            });

    }
);



document.addEventListener(
    "mouseout",
    function(event) {

        const entity =
            event.target.closest(".entity");


        if (!entity) return;


        document
            .querySelectorAll(".entity")
            .forEach(other => {

                other.classList.remove(
                    "entity-highlight"
                );

            });

    }
);





//
// Click popup
//

document.addEventListener(
    "click",
    function(event) {

        const entity =
            event.target.closest(".entity");


        if (!entity) {

            closeDefinitionPopup();

            return;
        }


        if (activeEntity === entity) {

            closeDefinitionPopup();

            return;
        }


        showDefinitionPopup(entity);

    }
);





function showDefinitionPopup(entity) {


    closeDefinitionPopup();


    activeEntity = entity;


    const popup =
        document.createElement(
            "div"
        );


    popup.className =
        "entity-popup";



    popup.innerHTML = `

        <div class="entity-popup-title">
            ${entity.dataset.entity}
        </div>


        <div class="entity-popup-meta">
            ${entity.dataset.type}
            |
            ${entity.dataset.scope}
        </div>


        <div class="entity-popup-description">
            ${
                entity.dataset.description ||
                "No description available"
            }
        </div>

    `;



    document.body.appendChild(
        popup
    );



    const rect =
        entity.getBoundingClientRect();



    popup.style.left =
        `${
            rect.left +
            window.scrollX
        }px`;



    popup.style.top =
        `${
            rect.bottom +
            window.scrollY +
            8
        }px`;

}





function closeDefinitionPopup() {


    const popup =
        document.querySelector(
            ".entity-popup"
        );


    if (popup) {

        popup.remove();

    }


    activeEntity = null;

}
