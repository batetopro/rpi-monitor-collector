function format_interval(ts){
    var seconds_in_day = 24 * 60 * 60,
        day_seconds = ts % seconds_in_day,
        days = (ts - day_seconds) / seconds_in_day,
        view = '';

    if (days > 0){
        view += days + ' days ';
    }

    var hour_seconds = day_seconds % 3600,
        hours = (day_seconds - hour_seconds) / 3600;

    if (hours < 10){
        hours = '0' + hours;
    }
    view += hours + ':';

    var minute_seconds = hour_seconds % 60,
    minutes = (hour_seconds - minute_seconds) / 60;

    if (minutes < 10){
        minutes = '0' + minutes;
    }
    view += minutes + ':';

    minute_seconds = Math.round(minute_seconds);

    if (minute_seconds < 10){
        minute_seconds = '0' + minute_seconds;
    }
    view += minute_seconds;

    return view;
};


var device_details = {
    url: undefined,
    usage_url: undefined,
    total_ram: undefined,
    render: function(is_init){
        $.getJSON(device_details.url, {}, function(resp){
            // console.log(resp);
            
            if (is_init) {
                device_usage.build();
            }

            device_details.total_ram = resp.total_ram;

            device_details.show_hostname(resp.hostname);
            device_details.show_status(resp.connection.status, resp.connection.state);
            device_details.show_cpu_temperature(resp.cpu_temperature);
            device_details.show_cpu_usage(resp.cpu_usage);
            device_details.show_cpu_frequency(resp.cpu_frequency);
            device_details.show_disk_io(resp.disk_io_read_bytes, resp.disk_io_write_bytes);
            device_details.show_disk_space(resp.disk_space_available, resp.disk_space_used, resp.disk_space_total);
            device_details.show_network_io(resp.network_io_received_bytes, resp.network_io_sent_bytes);
            device_details.show_swap_memory(resp.used_swap, resp.total_swap)
            device_details.show_used_ram(resp.used_ram, resp.total_ram);
            device_details.show_last_seen(resp.last_seen);
            device_details.show_time_on_host(resp.time_on_host);
            device_details.show_last_boot(resp.up_since);
            device_details.show_up_for(resp.up_for);
            device_details.show_error_message(resp.error_message);
            device_details.show_disk_partitions(resp.disk_partitions);
            device_details.show_net_io_counters(resp.net_io_counters);

            setTimeout(function(){
                device_details.render(false);
            }, 1000);
        });
    },

    show_cpu_frequency: function(cpu_frequency){
        if (cpu_frequency){
            $('#cpu-frequency').text(cpu_frequency + ' MHz')
        } else {
            $('#cpu-frequency').text('--')
        }
    },

    show_cpu_temperature: function(cpu_temperature){
        if (cpu_temperature){
            $('#cpu-temperature').text(cpu_temperature + ' C');
            if (cpu_temperature >= 85){
                // $('#cpu-temperature').removeClass('bg-secondary').removeClass('bg-warning').addClass('bg-danger');
            } else if (cpu_temperature >= 70) {
                // $('#cpu-temperature').removeClass('bg-secondary').addClass('bg-warning').removeClass('bg-danger');
            } else {
                // $('#cpu-temperature').addClass('bg-secondary').removeClass('bg-warning').removeClass('bg-danger');
            }

            $('#cpu-temperature-progresbar').parent().show();
            $('#cpu-temperature-progresbar').attr({
                'aria-valuenow': cpu_temperature,
                'aria-valuemin': 0,
                'aria-valuemax': 100,
            }).css({
                'width': cpu_temperature + '%',
            });

            if (cpu_temperature >= 85){
                // $('#cpu-usage').removeClass('bg-light').removeClass('bg-warning').addClass('bg-danger');
                $('#cpu-temperature-progresbar').removeClass('bg-primary').removeClass('bg-warning').addClass('bg-danger');
            } else if (cpu_temperature >= 70) {
                // $('#cpu-usage').removeClass('bg-light').addClass('bg-warning').removeClass('bg-danger');
                $('#cpu-temperature-progresbar').removeClass('bg-primary').addClass('bg-warning').removeClass('bg-danger');
            } else {
                // $('#cpu-usage').addClass('bg-light').removeClass('bg-warning').removeClass('bg-danger');
                $('#cpu-temperature-progresbar').addClass('bg-primary').removeClass('bg-warning').removeClass('bg-danger');
            }
        } else {
            $('#cpu-temperature').text('--');
            // $('#cpu-temperature').removeClass('bg-secondary').removeClass('bg-warning').removeClass('bg-danger');
        }
    },

    show_cpu_usage: function(cpu_usage){
        if (cpu_usage !== null){
            $('#cpu-usage').text(cpu_usage + ' %');
            
            $('#cpu-progresbar').parent().show();
            $('#cpu-progresbar').attr({
                'aria-valuenow': cpu_usage,
                'aria-valuemin': 0,
                'aria-valuemax': 100,
            }).css({
                'width': cpu_usage + '%',
            });

            if (cpu_usage >= 85){
                // $('#cpu-usage').removeClass('bg-light').removeClass('bg-warning').addClass('bg-danger');
                $('#cpu-progresbar').removeClass('bg-primary').removeClass('bg-warning').addClass('bg-danger');
            } else if (cpu_usage >= 70) {
                // $('#cpu-usage').removeClass('bg-light').addClass('bg-warning').removeClass('bg-danger');
                $('#cpu-progresbar').removeClass('bg-primary').addClass('bg-warning').removeClass('bg-danger');
            } else {
                // $('#cpu-usage').addClass('bg-light').removeClass('bg-warning').removeClass('bg-danger');
                $('#cpu-progresbar').addClass('bg-primary').removeClass('bg-warning').removeClass('bg-danger');
            }
        } else {
            $('#cpu-progresbar').parent().hide();
            $('#cpu-usage').text('--');
            // $('#cpu-usage').removeClass('bg-light').removeClass('bg-warning').removeClass('bg-danger');
        }
    },
    show_disk_io: function(read, write){
        if (read !== null){
            $('#disk-io-read').text(
                (read / (1024 * 1024 * 1024)).toFixed(2) + ' GBi'
            )
        } else {
            $('#disk-io-read').text('--')
        }

        if (write !== null){
            $('#disk-io-write').text(
                (write / (1024 * 1024 * 1024)).toFixed(2) + ' GBi'
            )
        } else {
            $('#disk-io-write').text('--')
        }
    },
    show_disk_partitions: function(partitions){
        if (partitions === null){
            $('#storage-space').html('<div class="alert bg-info">Information about storge space is not collected yet.</div>');
            $('#storage-io').html('<div class="alert bg-info">Information about storge space is not collected yet.</div>');
            return;
        }

        var space_view = '',
            io_view = '',
            total_space_available = 0,
            total_space_used = 0,
            total_space = 0,
            total_io_read_bytes = 0,
            total_io_read_count = 0,
            total_io_read_time = 0,
            total_io_write_bytes = 0,
            total_io_write_count = 0,
            total_io_write_time = 0;
        
        space_view += '<table class="table mb-0">';
        space_view += '<tr class="table-primary"><th>Device</th>';
        space_view += '<th class="text-center">Used</th>'
        space_view += '<th class="text-center">Available</th>'
        space_view += '<th class="text-center">Total</th>'
        space_view += '</tr>';
        

        io_view += '<table class="table mb-0">';
        io_view += '<tr class="table-primary"><th>Device</th><th>&nbsp;</th>';
        io_view += '<th class="text-center">Bytes</th>'
        io_view += '<th class="text-center">Count</th>'
        io_view += '<th class="text-center">Time</th>'
        io_view += '</tr>';

        
        for (var i = 0; i < partitions.length ; i++){
            var partition = partitions[i],
                space_available = (partition.space_available / (1024 * 1024 * 1024)).toFixed(2) + ' GBi',
                space_used = (partition.space_used / (1024 * 1024 * 1024)).toFixed(2) + ' GBi',
                space_total = (partition.space_total / (1024 * 1024 * 1024)).toFixed(2) + ' GBi',
                space_usage = ((partition.space_used / partition.space_available) * 100).toFixed(2),
                space_badge = (space_usage >= 85) ? 'bg-danger' : (space_usage >= 70) ? 'bg-warning' : 'bg-primary',
                io_read_bytes = (partition.io_read_bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GBi',
                io_write_bytes = (partition.io_write_bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GBi';
                header = '';
            
            total_space_available += partition.space_available;
            total_space_used += partition.space_used;
            total_space += partition.space_total;
            
            total_io_read_bytes += partition.io_read_bytes;
            total_io_read_count += partition.io_read_count;
            total_io_read_time += partition.io_read_time;
            total_io_write_bytes += partition.io_write_bytes;
            total_io_write_count += partition.io_write_count;
            total_io_write_time += partition.io_write_time;

            header = '<h5 title="' + partition.opts + '">' + partition.device + '</h5>'
            header += '<div class="progress mb-0">' + 
                '<div class="progress-bar ' + space_badge + '" role="progressbar" aria-valuenow="' + space_usage + '" aria-valuemin="0" aria-valuemax="100" style="width: ' + space_usage + '%;"></div>' + 
                '</div>';
            header += 'Mountpoint: <strong>' + partition.mountpoint + '</strong><br>'
            header += 'Type: <strong>' + partition.fstype + '</strong><br>'
            
            space_view += '<tr>'
            space_view += '<td width="240">' + header + '</td>';
            space_view += '<td class="text-center">' + space_available + '</td>';
            space_view += '<td class="text-center">' + space_used + '</td>';
            space_view += '<td class="text-center">' + space_total + '</td>';
            space_view += '</tr>'
            
            
            io_view += '<tr>'
            io_view += '<td width="240" rowspan="2">' + header + '</td>';
            io_view += '<th class="text-center">Read</th>';
            io_view += '<td class="text-center">' + io_read_bytes + '</td>';
            io_view += '<td class="text-center">' + partition.io_write_count + '</td>';
            io_view += '<td class="text-center">' + format_interval(partition.io_read_time / 1000) + '</td>';
            io_view += '</tr>'
            
            io_view += '<tr>'
            io_view += '<th class="text-center">Write</th>';
            io_view += '<td class="text-center">' + io_write_bytes + '</td>';
            io_view += '<td class="text-center">' + partition.io_read_count + '</td>';
            io_view += '<td class="text-center">' + format_interval(partition.io_write_time / 1000) + '</td>';
            io_view += '</tr>'
        }

        space_view += '<tr class="table-primary"><th>&nbsp;</th>';
        space_view += '<th class="text-center">' + (total_space_used / (1024 * 1024 * 1024)).toFixed(2) + ' GBi' + '</th>'
        space_view += '<th class="text-center">' + (total_space_available / (1024 * 1024 * 1024)).toFixed(2) + ' GBi' + '</th>'
        space_view += '<th class="text-center">' + (total_space / (1024 * 1024 * 1024)).toFixed(2) + ' GBi' + '</th>'
        space_view += '</tr>';
        space_view += '</table>'


        io_view += '<tr class="table-primary"><th rowspan="2">&nbsp;</th>';
        io_view += '<th class="text-center">Read</th>'
        io_view += '<th class="text-center">' + (total_io_read_bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GBi' + '</th>'
        io_view += '<th class="text-center">' + total_io_read_count + '</th>'
        io_view += '<th class="text-center">' + format_interval(total_io_read_time / 1000) + '</th>'
        io_view += '</tr>';

        io_view += '<tr class="table-primary">';
        io_view += '<th class="text-center">Weite</th>'
        io_view += '<th class="text-center">' + (total_io_write_bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GBi' + '</th>'
        io_view += '<th class="text-center">' + total_io_write_count + '</th>'
        io_view += '<th class="text-center">' + format_interval(total_io_write_time / 1000) + '</th>'
        io_view += '</tr>';

        io_view += '</table>'

        $('#storage-space').html(space_view);
        $('#storage-io').html(io_view);
    },
    show_disk_space: function(available, used, total){
        if (available !== null){
            $('#available-space').text(
                (available / (1024 * 1024 * 1024)).toFixed(2) + ' GBi'
            )
        } else {
            $('#available-space').text('--')
        }

        if (used !== null){
            $('#used-space').text(
                (used / (1024 * 1024 * 1024)).toFixed(2) + ' GBi'
            )
        } else {
            $('#used-space').text('--')
        }

        if (total !== null){
            $('#total-space').text(
                (total / (1024 * 1024 * 1024)).toFixed(2) + ' GBi'
            )
        } else {
            $('#total-space').text('--')
        }

        if (total !== null && used !== null){
            var used_percent = (used / total * 100).toFixed(2);
            $('#space-progresbar').parent().show();
            $('#space-progresbar').attr({
                'aria-valuenow': used,
                'aria-valuemin': 0,
                'aria-valuemax': total,
            }).css({
                'width': used_percent + '%',
            });
            
            if (used_percent >= 85){
                $('#space-progresbar').removeClass('bg-primary').removeClass('bg-warning').addClass('bg-danger');
            } else if (used_percent >= 70) {
                $('#space-progresbar').removeClass('bg-primary').addClass('bg-warning').removeClass('bg-danger');
            } else {
                $('#space-progresbar').addClass('bg-primary').removeClass('bg-warning').removeClass('bg-danger');
            }
        } else {
            $('#space-progresbar').parent().hide();
        }
    },
    show_error_message: function(message){
        if (message){
            $('#error-message').text(message).show();
        } else {
            $('#error-message').hide();
        }
    },
    show_hostname: function(hostname){
        $('#breadcrumb-navbar .breadcrumb-item.active').text(hostname);
    },
    show_last_seen: function(last_seen){
        if (last_seen !== null){
            $('#last-seen').text(
                moment.unix(last_seen).fromNow()
            );
        } else {
            $('#last-seen').text('--');
        }
    },
    show_last_boot: function(last_boot_on){
        if (last_boot_on !== null){
            $('#up-since').text(
                moment.unix(last_boot_on).format('YYYY-MM-DD HH:mm:ss')
            );
        } else {
            $('#up-since').text('--');
        }
    },
    show_net_io_counters: function(io_counters){
        if (io_counters === null){
            $('#network-io').html('<div class="alert bg-info">Information about network I/O is not collected yet.</div>');
            return;
        }

        var rows = [
                {'title': 'Interface', 'field': 'name'},
                {'title': 'Sent bytes', 'field': 'bytes_sent'},
                {'title': 'Sent packets', 'field': 'packets_sent'},
                {'title': 'Drop-in', 'field': 'dropin'},
                {'title': 'Errors in', 'field': 'errin'},
                {'title': 'Received bytes', 'field': 'bytes_recv'},
                {'title': 'Received packets', 'field': 'packets_recv'},
                {'title': 'Drop out', 'field': 'dropout'},
                {'title': 'Errors out', 'field': 'errout'},
            ],
            keys = Object.keys(io_counters);
        
        
        var view = '<div class="clearfix"><div class="float-start">';
        view += '<table class="table mb-0">'
        for(var i = 0; i < rows.length; i++){
            view += '<tr class="table-primary"><th class="text-center" width="140">' + rows[i].title + '</th?</tr>'
        }
        view += '</table></div>'
        view += '<div class="network-counters">'
        view += '<table class="table mb-0">'

        for(var i = 0; i < rows.length ;i++){
            var row = rows[i];
            
            if (row.field == 'name'){
                view += '<tr class="table-primary">';
            } else {
                view += '<tr>';
            }

            for(var j = 0; j < keys.length; j++){
                if (row.field == 'name'){
                    view += '<th class="text-center" width="400">' + keys[j] + '</th>';
                } else {
                    view += '<td class="text-center">' + io_counters[keys[j]][row.field] + '</td>';
                }
            }

            view += '</tr>';
        }

        view += '</table></div>'
        view += '</div>'

        $('#network-io').html(view);
    },
    show_network_io: function(received, sent){
        if (received !== null){
            $('#network-received').text(
                (received / (1024 * 1024 * 1024)).toFixed(2) + ' GBi'
            )
        } else {
            $('#network-received').text('--');
        }

        if (sent !== null){
            $('#network-sent').text(
                (sent / (1024 * 1024 * 1024)).toFixed(2) + ' GBi'
            )
        } else {
            $('#network-sent').text('--');
        }
    },    
    show_status: function(connection_status, connection_state){
        if (connection_status == 'enabled'){
            if (connection_state == 'connected'){
                $('#device-status').addClass('bg-success').removeClass('bg-danger').removeClass('bg-secondary');
            } else {
                $('#device-status').addClass('bg-danger').removeClass('bg-success').removeClass('bg-secondary');
            }
            $('#device-status').text(connection_state);
        } else {
            $('#device-status').addClass('bg-secondary').removeClass('bg-success').removeClass('bg-danger');
            $('#device-status').text(connection_status);
        }
    },
    show_swap_memory: function(used_swap, total_swap){
        if (used_swap !== null) {
            $('#used-swap').text(
                (used_swap / (1024 * 1024)).toFixed(2) + ' MBi'
            );
        } else {
            $('#used-swap').text('--');
        }
        
        if (total_swap !== null) {
            $('#total-swap').text(
                (total_swap / (1024 * 1024)).toFixed(2) + ' MBi'
            );
        } else {
            $('#total-swap').text('--');
        }
    },
    show_time_on_host: function(time_on_host){
        if (time_on_host !== null){
            $('#time-on-host').text(
                moment.unix(time_on_host).format('YYYY-MM-DD HH:mm:ss')
            );
        } else {
            $('#time-on-host').text('--');
        }
    },
    show_up_for: function(up_for){
        if (up_for !== null){
            var view = format_interval(up_for);
            $('#up-for').text(view);
        } else {
            $('#up-for').text('--');
        }
    },
    show_used_ram: function(used_ram, total_ram){
        if (used_ram !== null){
            $('#used-ram').text(
                (used_ram / (1024 * 1024)).toFixed(2) + ' MBi'
            );
            
            if (total_ram === null) {
                var used_ram_percent = 0;
            } else {
                var used_ram_percent = ((used_ram / total_ram) * 100).toFixed(2);
            }

            $('#ram-progresbar').parent().show();
            $('#ram-progresbar').attr({
                'aria-valuenow': used_ram_percent,
                'aria-valuemin': 0,
                'aria-valuemax': 100,
            }).css({
                'width': used_ram_percent + '%',
            });

            if (used_ram_percent >= 85){
                $('#ram-progresbar').removeClass('bg-primary').removeClass('bg-warning').addClass('bg-danger');
                // $('#used-ram').removeClass('bg-secondary').removeClass('bg-warning').addClass('bg-danger');
            } else if (used_ram_percent >= 70) {
                // $('#used-ram').removeClass('bg-secondary').addClass('bg-warning').removeClass('bg-danger');
                $('#ram-progresbar').removeClass('bg-primary').addClass('bg-warning').removeClass('bg-danger');
            } else {
                // $('#used-ram').addClass('bg-secondary').removeClass('bg-warning').removeClass('bg-danger');
                $('#ram-progresbar').addClass('bg-primary').removeClass('bg-warning').removeClass('bg-danger');
            }
        } else {
            $('#ram-progresbar').parent().hide();
            $('#used-ram').text('--');
            // $('#used-ram').removeClass('bg-secondary').removeClass('bg-warning').removeClass('bg-danger');
        }
    }
}

var device_usage = {
    primary_color: 'rgb(39,128,227)',
    secondary_color: 'rgb(55,58,60)',
    grid_color: '#e9ecef',

    cpu_chart: undefined,
    current_disc_io_read: undefined,
    current_disc_io_write: undefined,
    current_network_io_read: undefined,
    current_network_io_write: undefined,
    disc_chart: undefined,
    network_chart: undefined,
    ram_chart: undefined,
    build: function(){
        device_usage.current_disc_io_read = undefined;
        device_usage.current_disc_io_write = undefined;
        device_usage.current_network_io_read = undefined;
        device_usage.current_network_io_write = undefined;

        $.get(device_details.usage_url, {}, function(resp){
            resp = device_usage.parse_response(resp);
            device_usage.build_cpu_chart(
                resp.time_saved,
                resp.cpu_usage,
                resp.cpu_temperature
            );
            device_usage.build_ram_chart(
                resp.time_saved,
                resp.used_ram
            );
            device_usage.build_disc_io_chart(
                resp.time_saved,
                resp.disc_io_read,
                resp.disc_io_write
            );
            device_usage.build_network_chart(
                resp.time_saved,
                resp.network_io_read,
                resp.network_io_write
            )

            // console.log(resp);

            // TODO: make this better
            setTimeout(function(){
                device_usage.build()
            }, 1000)
        });
    },
    build_cpu_chart: function(time_saved, cpu_usage, cpu_temperature){
        if (time_saved.length < 1){
            return;
        }

        $('#cpu-performance').html('<div style="height: 200px"><canvas id="cpu-diagram"></canvas></div>');

        const data = {
            labels: time_saved,
            datasets: [
                {
                    label: 'CPU Usage %',
                    data: cpu_usage,
                    borderColor: device_usage.primary_color,
                    // borderColor: 'rgb(75, 192, 192)',
                    // tension: 0.1
                },
                {
                    label: 'CPU Temperature C',
                    data: cpu_temperature,
                    borderColor: device_usage.secondary_color,
                    // borderColor: 'rgb(75, 192, 192)',
                    // tension: 0.1
                }
            ]
        };

        const config = {
            type: 'line',
            data: data,
            options: {
                animations: false,
                elements: {
                    point: {
                        radius: 0
                    }
                },
                maintainAspectRatio: false,
                plugins: {
                    tooltip: {
                        enabled: false,
                    }
                },
                responsive: true,
                scales: {
                    y: {
                        min: 0,
                        max: 100,
                        grid: {
                            display: true,
                            drawOnChartArea: true,
                            color: device_usage.grid_color,
                        },
                        ticks: {
                            stepSize: 10,
                            autoSkip: false,
                            callback: function (value, index) {
                                return value;
                            }
                        }
                    },
                    x: {
                        type: 'linear',
                        min: time_saved[0],
                        max: time_saved[time_saved.length - 1],
                        grid: {
                            display: true,
                            drawOnChartArea: true,
                            color: device_usage.grid_color,
                        },
                        ticks: {
                            callback: function(value, index) {
                                return device_usage.format_time_saved(value);
                            },
                            autoSkip: false,
                            maxRotation: 0,
                        },
                    },
                }
            },
        };
        
        const ctx = document.getElementById('cpu-diagram');

        device_usage.cpu_chart = new Chart(ctx, config);
    },
    build_disc_io_chart: function(time_saved, read_io, write_io){
        if (time_saved.length <= 1){
            return;
        }

        $('#disc-performance').html('<div style="height: 200px"><canvas id="disc-diagram"></canvas></div>');

        const data = {
            labels: Array.from(time_saved).slice(1),
            datasets: [
                {
                    label: 'Read',
                    data: read_io,
                    borderColor: device_usage.primary_color,
                    // borderColor: 'rgb(75, 192, 192)',
                    // tension: 0.1
                },
                {
                    label: 'Write',
                    data: write_io,
                    borderColor: device_usage.secondary_color,
                    // borderColor: 'rgb(75, 192, 192)',
                    // tension: 0.1
                },
            ]
        };

        const config = {
            type: 'line',
            data: data,
            options: {
                animations: false,
                elements: {
                    point: {
                        radius: 0
                    }
                },
                maintainAspectRatio: false,
                plugins: {
                    tooltip: {
                        enabled: false,
                    }
                },
                responsive: true,
                scales: {
                    y: {
                        min: 0,
                        // max: device_details.total_ram,
                        grid: {
                            display: true,
                            drawOnChartArea: true,
                            color: device_usage.grid_color,
                        },
                        ticks: {
                            autoSkip: false,
                            // count: 8,
                            callback: function (value, index, values) {
                                return Math.round(value / (1024 * 100)) * 100;
                            }
                        }
                    },
                    x: {
                        type: 'linear',
                        min: time_saved[0],
                        max: time_saved[time_saved.length - 1],
                        grid: {
                            display: true,
                            drawOnChartArea: true,
                            color: device_usage.grid_color,
                        },
                        ticks: {
                            callback: function(value, index) {
                                return device_usage.format_time_saved(value);
                            },
                            autoSkip: false,
                            maxRotation: 0,
                        },
                    },
                }
            },
        };
        
        const ctx = document.getElementById('disc-diagram');

        device_usage.disc_chart = new Chart(ctx, config);
    },
    
    build_network_chart: function(time_saved, received, sent){
        if (time_saved.length <= 1){
            return;
        }

        $('#network-performance').html('<div style="height: 200px"><canvas id="network-diagram"></canvas></div>');

        const data = {
            labels: Array.from(time_saved).slice(1),
            datasets: [
                {
                    label: 'Received',
                    data: received,
                    borderColor: device_usage.primary_color,
                    // borderColor: 'rgb(75, 192, 192)',
                    // tension: 0.1
                },
                {
                    label: 'Transmitted',
                    data: sent,
                    borderColor: device_usage.secondary_color,
                    // borderColor: 'rgb(75, 192, 192)',
                    // tension: 0.1
                },
            ]
        };

        const config = {
            type: 'line',
            data: data,
            options: {
                animations: false,
                elements: {
                    point: {
                        radius: 0
                    }
                },
                maintainAspectRatio: false,
                plugins: {
                    tooltip: {
                        enabled: false,
                    }
                },
                responsive: true,
                scales: {
                    y: {
                        grid: {
                            display: true,
                            drawOnChartArea: true,
                            color: device_usage.grid_color,
                        },
                        ticks: {
                            autoSkip: false,
                            count: 8,
                            callback: function (value, index) {
                                // return value
                                return Math.round(value / (1024 * 100)) * 100;
                            }
                        }
                    },
                    x: {
                        type: 'linear',
                        min: time_saved[0],
                        max: time_saved[time_saved.length - 1],
                        grid: {
                            display: true,
                            drawOnChartArea: true,
                            color: device_usage.grid_color,
                        },
                        ticks: {
                            callback: function(value, index) {
                                return device_usage.format_time_saved(value);
                            },
                            autoSkip: false,
                            maxRotation: 0,
                        },
                    },
                }
            },
        };
        
        const ctx = document.getElementById('network-diagram');

        device_usage.network_chart = new Chart(ctx, config);
    },
    build_ram_chart: function(time_saved, used_ram){
        if (time_saved.length < 1){
            return;
        }

        $('#ram-performance').html('<div style="height: 200px"><canvas id="ram-diagram"></canvas></div>');

        const data = {
            labels: Array.from(time_saved).slice(1),
            datasets: [
                {
                    label: 'Used RAM MBi',
                    data: used_ram,
                    borderColor: device_usage.primary_color,
                    // borderColor: 'rgb(75, 192, 192)',
                    // tension: 0.1
                },
            ]
        };

        const config = {
            type: 'line',
            data: data,
            options: {
                animations: false,
                elements: {
                    point: {
                        radius: 0
                    }
                },
                maintainAspectRatio: false,
                plugins: {
                    tooltip: {
                        enabled: false,
                    }
                },
                responsive: true,
                scales: {
                    y: {
                        min: 0,
                        max: device_details.total_ram,
                        grid: {
                            display: true,
                            drawOnChartArea: true,
                            color: device_usage.grid_color,
                        },
                        ticks: {
                            autoSkip: false,
                            count: 8,
                            callback: function (value, index, values) {
                                return Math.round(value / (1024 * 1024 * 100)) * 100;
                            }
                        }
                    },
                    x: {
                        type: 'linear',
                        min: time_saved[0],
                        max: time_saved[time_saved.length - 1],
                        grid: {
                            display: true,
                            drawOnChartArea: true,
                            color: device_usage.grid_color,
                        },
                        ticks: {
                            callback: function(value, index) {
                                return device_usage.format_time_saved(value);
                            },
                            autoSkip: false,
                            maxRotation: 0,
                        },
                    },
                }
            },
        };
        
        const ctx = document.getElementById('ram-diagram');

        device_usage.cpu_chart = new Chart(ctx, config);
    },
    format_time_saved: function(value){
        if (!value){
            return;
        }

        var ts = new Date(value * 1000);
        var minutes = ts.getMinutes();
        if (minutes < 10){
            minutes = '0' + minutes;
        }
        var hours = ts.getHours()
        if (hours < 10){
            hours = '0' + hours;
        }
        return hours + ':' + minutes;
    },
    parse_response: function(resp){
        var result = {
                'time_saved': [],
                'cpu_usage': [],
                'cpu_temperature': [],
                'used_ram': [],
                'disc_io_read': [],
                'disc_io_write': [],
                'network_io_read': [],
                'network_io_write': [],
            },
            lines = resp.split('\n');

        for(var i = 0; i < lines.length; i++){
            if (!lines[i]){
                continue;
            }

            var columns = lines[i].split(',');
            result.time_saved.push(parseFloat(columns[0]));
            result.cpu_temperature.push(parseFloat(columns[1]));
            result.cpu_usage.push(parseFloat(columns[2]));
            result.used_ram.push(parseFloat(columns[3]));

            var disc_io_read = parseFloat(columns[4]);
            if (device_usage.current_disc_io_read !== undefined){
                if (device_usage.current_disc_io_read <= disc_io_read){
                    result.disc_io_read.push(disc_io_read - device_usage.current_disc_io_read);
                } else {
                    result.disc_io_read.push(disc_io_read);
                }
            }
            device_usage.current_disc_io_read = disc_io_read;

            var disc_io_write = parseFloat(columns[5]);
            if (device_usage.current_disc_io_write !== undefined){
                if (device_usage.current_disc_io_write <= disc_io_write){
                    result.disc_io_write.push(disc_io_write - device_usage.current_disc_io_write);
                } else {
                    result.disc_io_write.push(disc_io_write);
                }
            }
            device_usage.current_disc_io_write = disc_io_write;

            var network_io_read = parseFloat(columns[6]);
            if (device_usage.current_network_io_read !== undefined){
                if (device_usage.current_network_io_read <= network_io_read){
                    result.network_io_read.push(network_io_read - device_usage.current_network_io_read);
                } else {
                    result.network_io_read.push(network_io_read);
                }
            }
            device_usage.current_network_io_read = network_io_read;

            var network_io_write = parseFloat(columns[7]);
            if (device_usage.current_network_io_write !== undefined){
                if (device_usage.current_network_io_write <= network_io_write){
                    result.network_io_write.push(network_io_write - device_usage.current_network_io_write);
                } else {
                    result.network_io_write.push(network_io_write);
                }
            }
            device_usage.current_network_io_write = network_io_write;
        }

        return result;
    }
}


var network_interfaces = {
    url: undefined,
    build: function(){
        network_interfaces.load();
        $('#net-interfaces-refresh').on('click', function(){
            network_interfaces.load();
        });
    },
    load: function(){
        $.getJSON(network_interfaces.url, {}, function(resp){
            var view = '';

            if (resp.length == 0){
                view = '<div class="alert bg-info">Information about network interfaces is not collected yet.</div>';
            } else {
                var view = '';

                for (var i = 0; i < resp.length; i++){
                    var interface = resp[i];
                    view += '<div class="clearfix">';
                    view += '<div class="float-start"><h4>' + interface.name + '</h4></div>'
                    if (interface.isup) {
                        view += '<div class="float-end"><span class="badge bg-success">UP</span></div>';
                    } else {
                        view += '<div class="float-end"><span class="badge bg-danger">DOWN</span></div>';
                    }
                    
                    view += '<table class="table mb-0">';
                    view += '<tr>';
                    view += '<td>MTU</td><th>' + interface.mtu + '</th>';
                    view += '<td>Spped</td><th>' + interface.speed + '</th>';
                    view += '<td>Duplex</td><th>' + interface.duplex + '</th>';
                    view += '</tr>';
                    view += '</table>';
                    
                    if (interface.addresses){
                        view += '<table class="table">';
                        view += '<tr class="table-primary">';
                        view += '<th class="text-center">Family</th>';
                        view += '<th class="text-center">Address</th>';
                        view += '<th class="text-center">Netmask</th>';
                        view += '<th class="text-center">Broadcast</th>';
                        view += '<th class="text-center">PTP</th>';
                        view += '</tr>';

                        for (var j = 0; j < interface.addresses.length; j++){
                            var address = interface.addresses[j],
                                netmask = (address.netmask) ? address.netmask : '--',
                                broadcast = (address.broadcast) ? address.broadcast : '--',
                                ptp = (address.ptp) ? address.ptp : '--';
                            view += '<tr>';
                            view += '<td class="text-center">' + address.family + '</td>';
                            view += '<td class="text-center">' + address.address + '</td>';
                            view += '<td class="text-center">' + netmask + '</td>';
                            view += '<td class="text-center">' + broadcast + '</td>';
                            view += '<td class="text-center">' + ptp + '</td>';
                            view += '</tr>'
                        }
                        view += '</table>';
                    }
                    view += '</div>';
                }
            }

            $('#network-interfaces').html(view);
        });
    }
};


