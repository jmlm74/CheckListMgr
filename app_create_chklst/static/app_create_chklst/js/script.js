import {SendAjax, getCookie, test2} from '../../../../static/js/modul.js'


// Declaration fonction qui permet d'intialiser le DOM pour le dragndrop
let dragndrop = () =>{
    if (document.querySelector('.dragndrop')) {
    /* ***************************** */
    /* * Beginning for drag-n-drop * */
    /* ***************************** */
        const draggables = document.querySelectorAll('.list-item')
        const containers = document.querySelectorAll('.list')

        draggables.forEach(draggable => {
          draggable.addEventListener('dragstart', () => {
            draggable.classList.add('dragging')
          })

          draggable.addEventListener('dragend', () => {
            draggable.classList.remove('dragging')
          })
        })

        containers.forEach(container => {
          container.addEventListener('dragover', e => {
            e.preventDefault()
            const afterElement = getDragAfterElement(container, e.clientY)
            const draggable = document.querySelector('.dragging')
            if (afterElement == null) {
              container.appendChild(draggable)
            } else {
              container.insertBefore(draggable, afterElement)
            }
          })
        })

        function getDragAfterElement(container, y) {
          const draggableElements = [...container.querySelectorAll('.list-item:not(.dragging)')]

          return draggableElements.reduce((closest, child) => {
            const box = child.getBoundingClientRect()
            const offset = y - box.top - box.height / 2
            if (offset < 0 && offset > closest.offset) {
              return { offset: offset, element: child }
            } else {
              return closest
            }
          }, { offset: Number.NEGATIVE_INFINITY }).element
        }
    /* *********************** */
    /* * End for drag-n-drop * */
    /* *********************** */
    }
}

/***************************/
/* create/update checklist */
/***************************/
if ((document.getElementById('createchklst'))||(document.getElementById('updatechklst')) ){   // create checklist page
    console.log("JS createchklst-updatechecklst loaded");
    const csrfToken = getCookie('csrftoken');
    const select_heading = document.getElementById("select_heading")
    const my_categories = document.getElementById("categories")
    const my_lines = document.getElementById("lines")

    select_heading.addEventListener('change', e => {
        let x = select_heading.value;
        let my_class = `heading_${x}`;
        let all_categories = my_categories.querySelectorAll(":scope > .cat-item");
        let all_lines = my_lines.querySelectorAll(":scope > .line-item");
        if (x == "0"){
           all_categories.forEach( elt => elt.style.visibility = "visible");
           all_lines.forEach( elt => elt.style.visibility = "visible");
           return;
        }
        let my_selected_categories =  my_categories.querySelectorAll(":scope > ."+my_class);
        let my_selected_lines =  my_lines.querySelectorAll(":scope > ."+my_class);
        all_categories.forEach( elt => elt.style.visibility = "hidden");
        my_selected_categories.forEach(elt => {
           elt.style.visibility = "visible";
           let cloned_elt = elt.cloneNode(true);
           my_categories.insertBefore(cloned_elt, my_categories.firstChild);
           my_categories.removeChild(elt);
        })
        all_lines.forEach( elt => elt.style.visibility = "hidden");
        my_selected_lines.forEach(elt => {
           elt.style.visibility = "visible";
           let cloned_elt = elt.cloneNode(true);
           my_lines.insertBefore(cloned_elt, my_lines.firstChild);
           my_lines.removeChild(elt);
        })

        // Reinit du dragndrop car le DOM a été modifié
        dragndrop();
    });

    // submit the form --> Ajax
    // update or create checklist
    document.getElementById('submit-btn').addEventListener('click', e => {
        let chklst_items = document.getElementById("chklst-items").children;
        let data = {};
        let chk = [];
        let chk_pos = 0;
        const my_array = ['cat', 'lin'];

        const chk_key = document.getElementById('id_chk_key').value;
        const chk_title = document.getElementById('id_chk_title').value;
        const chk_enable = document.getElementById('id_chk_enable').checked;

        if ((chk_key.length === 0) || (chk_title.length === 0) || (chk_enable.length === 0)) {
            alert(inputError);
            return false;
        }

        if (document.getElementById('id_chk_company')) {
            data['chk_company'] = document.getElementById('id_chk_company').value;

        }

        if (document.getElementById('createchklst')){
            data['action'] = 'create'  // create checklist
        }
        else {
            data['action'] = 'update'  // update checklist
        }

        data['chk_key'] = document.getElementById('id_chk_key').value;
        data['chk_title'] = document.getElementById('id_chk_title').value;
        data['chk_enable'] = document.getElementById('id_chk_enable').checked;

        // console.log(`${chk_key} - ${chk_title} - ${chk_enable}`)
        for (let i = 0; i < chklst_items.length; i++) {
            let my_id = chklst_items[i].id.substring(0, 3);
            console.log(my_id)
            if (my_array.includes(my_id)) {
                chk[chk_pos] = chklst_items[i].id;
                chk_pos++;
            }
        }
        data['lines'] = chk;
        // console.log(data)
        data = JSON.stringify(data);
        // ici send ajax
        SendAjax('POST', '/app_create_chklst/create_chklst/', data, csrfToken)
            .done(function () {
                window.location.replace(returnURL)
            })
            .fail(function (response) {
                console.error("Erreur Ajax : " + response.data);
                alert("Erreur Ajax - " + response.data);
            });

    });
}

// Initialisation du dragndrop
dragndrop();

/* *********************** */
/* * Beginning Modal box * */
/* *********************** */
// if category, line or headings
if ((document.getElementById('catandlinemgmt')) || (document.getElementById('main')) ||
    (document.getElementById('create-heading'))) {    //category and line management page
//JQuery is used for BSModal (Bootstrap)
    $(function () {
        console.log("Jquery loaded!!!!!")
        // console.log(formURL)
        // console.log(formURL2)
        $("#create-cat").modalForm({
            formURL: formURL,
            modalID: "#create-modal"
        });

        $("#create-line").modalForm({
            formURL: formURL2,
            modalID: "#create-modal"
        });

        $("#create-heading").modalForm({
            formURL: formURLCreate,
            modalID: "#create-modal"
        });

        $(".bs-modal").each(function () {
            $(this).modalForm(
                {
                    formURL: $(this).data("form-url"),
                    modalID: "#modal"
                });
            console.log(`formUrl = ${formURL}`)
        });
    });

}
/* ********************* */
/* * Beginning end box * */
/* ********************* */