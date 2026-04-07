
(function() {
    function getApiBaseUrl() {
        const protocol = window.location.protocol;
        const hostname = window.location.hostname;
        const port = window.location.port;
        
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            return 'window.API_BASE_URL';
        }
        
        if (protocol === 'https:') {
            return protocol + '//' + hostname;
        }
        
        return protocol + '//' + hostname + (port ? ':' + port : '');
    }
    
    window.API_BASE_URL = getApiBaseUrl();
})();
