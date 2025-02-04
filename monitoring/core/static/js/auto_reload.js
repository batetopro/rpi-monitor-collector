function autoRefreshPage() {
    window.location = window.location.href;
}
setInterval('autoRefreshPage()', 5000);