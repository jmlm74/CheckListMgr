"use strict";
console.log("base corejs loaded !");

/***********************************/
/* For compatibility with tables2  */
/* can't set redirection in table  */
/* --> build url here for bs-modal */
/***********************************/
// Display bs-modal
$(".Display-class").each(function () {
    let url=formURLDisplay+$(this).attr('id');
    url = url.slice(0,-1);  // remove last caracter idU to get the id
    $(this).modalForm({
        formURL: url,
        modalID: "#create-modal"
    });
});
// Update bs-modal
$(".Update-class").each(function () {
    let url=formURLUpdate+$(this).attr('id');
    url = url.slice(0,-1);  // remove last caracter idU to get the id
    $(this).modalForm({
        formURL: url,
        modalID: "#create-modal"
    });
});
// Remove bs-modal
$(".Remove-class").each(function () {
    let url=formURLRemove+$(this).attr('id');
    url = url.slice(0,-1);  // remove last caracter idU to get the id
    $(this).modalForm({
        formURL: url,
        modalID: "#create-modal"
    });
});
