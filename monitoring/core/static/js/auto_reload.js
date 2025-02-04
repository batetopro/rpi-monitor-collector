function autoRefreshPage() {
    window.location = window.location.href;
}

if (!window.location.href.endsWith('change/')){
    setInterval('autoRefreshPage()', 5000);
}
