/* *********************** */
/* * Beginning Modal box * */
/* *********************** */
if ((document.getElementById('mgrmgmt')) || (document.getElementById('main'))) {    // manager page
//JQuery is used for BSModal (Bootstrap)
    $(function () {
        console.log("Jquery loaded!!!!!")
        // console.log(formURL)
        // console.log(formURL2)
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

        /***********************************/
        /* For compatibility with tables2  */
        /* can't set redirection in table  */
        /* --> build url here for bs-modal */
        /***********************************/
        // Display Manager
        $(".Display-class").each(function () {
            let url=formURLDisplay+$(this).attr('id');
            url = url.slice(0,-1);  // remove last caracter idU to get the id
            $(this).modalForm({
                formURL: url,
                modalID: "#create-modal"
            });
        });
        // Update Manager
        $(".Update-class").each(function () {
            let url=formURLUpdate+$(this).attr('id');
            url = url.slice(0,-1);  // remove last caracter idU to get the id
            $(this).modalForm({
                formURL: url,
                modalID: "#create-modal"
            });
        });
        // Remove manager
        $(".Remove-class").each(function () {
            let url=formURLRemove+$(this).attr('id');
            url = url.slice(0,-1);  // remove last caracter idU to get the id
            $(this).modalForm({
                formURL: url,
                modalID: "#create-modal"
            });
        });

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