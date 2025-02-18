var devices_table = {
    url: undefined,
    ssh_configurations_url: undefined,
    get_badge_class: function(usage){
        if (isNaN(usage) || usage === null){
            return '';
        } else if (usage >= 85){
            return 'badge bg-warning';
        } else if (usage >= 70){
            return 'badge bg-danger';
        } else {
            return 'badge bg-secondary';
        }
    },
    render: function(){
        $.getJSON(devices_table.url, {}, function(resp){
            if (resp.hosts.length == 0) {
                $('#devices tbody').html(
                    '<tr><td colspan="6" class="text-center">' +
                    '<div class="alert alert-primary">No hosts found. <a href="' + 
                    devices_table.ssh_configurations_url + 
                    '">Go and create a connection</a> to your first host.</div></td></tr>'
                );
            } else {
                var view = '';
                for (var i = 0; i < resp.hosts.length; i++){
                    var host = resp.hosts[i];
                    
                    view += '<tr>';
                    view += '<td>';
                    view += '<strong><a href="' + host.change_link + '">' + host.hostname + '</a></strong><br>';
                    view += '<small>' + host.model + '</small>';
                    view += '</td>';

                    var state_class, state_text;

                    if (host.status == 'enabled'){
                        if (host.state == 'connected'){
                            state_class = 'bg-success';
                        } else {
                            state_class = 'bg-danger';
                        }
                        state_text = host.state;
                    } else {
                        state_text = host.status;
                        state_class = 'bg-secondary';
                    }

                    view += '<td><span class="badge ' + state_class + '">' + state_text + '</span></td>';

                    var used_ram = (host.used_ram !== null) ? (host.used_ram / (1024 * 1024)).toFixed(2) : '--',
                        total_ram = (host.total_ram !== null) ? (host.total_ram / (1024 * 1024)).toFixed(2) + ' MBi' : '--',
                        ram_usage = (host.used_ram / host.total_ram) * 100,
                        cpu_usage = (host.cpu_usage !== null) ? host.cpu_usage : '--',
                        cpu_temperature = (host.cpu_temperature !== null) ? host.cpu_temperature : '--',
                        used_storage = (host.used_storage !== null) ? (host.used_storage / (1024 * 1024 * 1024)).toFixed(2) : '--',
                        total_storage = (host.total_storage !== null) ? (host.total_storage / (1024 * 1024 * 1024)).toFixed(2) + ' GBi' : '--',
                        storage_usage = (host.used_storage / host.total_storage) * 100;

                    view += '<td><span class="' + devices_table.get_badge_class(ram_usage) + '">' + used_ram + ' / ' + total_ram + '</span></td>';
                    view += '<td><span class="' + devices_table.get_badge_class(host.cpu_usage) + '">' + cpu_usage + '</span></td>';
                    view += '<td><span class="' + devices_table.get_badge_class(host.cpu_temperature) + '">' + cpu_temperature + '</span></td>';
                    view += '<td><span class="' + devices_table.get_badge_class(storage_usage) + '">' + used_storage + ' / ' + total_storage + '</span></td>';

                    view += '</tr>';
                }

                $('#devices tbody').html(view);
            }
            setTimeout(function(){
                devices_table.render()
            }, 5000);
        });
    }
};
