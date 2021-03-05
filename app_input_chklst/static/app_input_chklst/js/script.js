/* *********************** */
/* * Beginning Modal box * */
/* *********************** */
if ((document.getElementById('mgrmgmt')) || (document.getElementById('main'))) {    // manager page
//JQuery is used for BSModal (Bootstrap)
    $(function () {
        console.log("Jquery loaded!!!!!")
        $("#create-mgr").modalForm({
            formURL: formURLCreate,
            modalID: "#create-modal-large"
        });
        $("#create-mat").modalForm({
            formURL: formURLCreate,
            modalID: "#create-modal"
        });
        $("#create-adr").modalForm({
            formURL: formURLCreate,
            modalID: "#create-modal-large"
        });

        // ICI BS_Modal

        $(".bs-modal-large").each(function () {
            $(this).modalForm(
                {
                    formURL: $(this).data("form-url"),
                    modalID: "#modal-large"
                });
        });

        $(".bs-modal").each(function () {
            $(this).modalForm(
                {
                    formURL: $(this).data("form-url"),
                    modalID: "#modal"
                });
        });

        // Hide message
        $(".alert").fadeTo(2000, 500).slideUp(500, function () {
            $(".alert").slideUp(500);
        });

    });
}
/* ********************* */
/* * Beginning end box * */
/* ********************* */