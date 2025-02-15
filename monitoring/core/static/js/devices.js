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
            if (resp.devices.length == 0) {
                $('#devices tbody').html(
                    '<tr><td colspan="6" class="text-center">' +
                    '<div class="alert alert-primary">No devices found. <a href="' + 
                    devices_table.ssh_configurations_url + 
                    '">Go and register</a> your first device.</div></td></tr>'
                );
            } else {
                var view = '';
                for (var i = 0; i < resp.devices.length; i++){
                    var device = resp.devices[i],
                        status_class;
                    
                    if (device.status == 'connected'){
                        status_class = 'bg-success';
                    } else if (device.status == 'disconnected'){
                        status_class = 'bg-danger';
                    } else {
                        status_class = 'bg-secondary';
                    }

                    view += '<tr>'
                    view += '<td><a href="' + device.change_link + '">' + device.hostname + '</a></td>';
                    view += '<td><span class="badge ' + status_class + '">' + device.status + '</span></td>';

                    var used_ram = (device.used_ram !== null) ? (device.used_ram / (1024 * 1024)).toFixed(2) : '--',
                        total_ram = (device.total_ram !== null) ? (device.total_ram / (1024 * 1024)).toFixed(2) + ' MBi' : '--',
                        ram_usage = (device.used_ram / device.total_ram) * 100,
                        cpu_usage = (device.cpu_usage !== null) ? device.cpu_usage : '--',
                        cpu_temperature = (device.cpu_temperature !== null) ? device.cpu_temperature : '--',
                        used_storage = (device.used_storage !== null) ? (device.used_storage / (1024 * 1024 * 1024)).toFixed(2) : '--',
                        total_storage = (device.total_storage !== null) ? (device.total_storage / (1024 * 1024 * 1024)).toFixed(2) + ' GBi' : '--',
                        storage_usage = (device.used_storage / device.total_storage) * 100;

                    view += '<td><span class="' + devices_table.get_badge_class(ram_usage) + '">' + used_ram + ' / ' + total_ram + '</span></td>';
                    view += '<td><span class="' + devices_table.get_badge_class(device.cpu_usage) + '">' + cpu_usage + '</span></td>';
                    view += '<td><span class="' + devices_table.get_badge_class(device.cpu_temperature) + '">' + cpu_temperature + '</span></td>';
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
