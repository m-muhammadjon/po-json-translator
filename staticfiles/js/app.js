// connect to the socket
const poSocket = new WebSocket(`ws://${window.location.host}/ws/`);
    // display the process status
    poSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        let tr_id = `file-${data["id"]}`;
        if (document.querySelector(`tr#${tr_id}`) == null)  {
              location.reload();
        } else {
            if (data['status'] == 'Processing') {
                // update the status and percentage
                document.querySelector(`tr#${tr_id} td.status`).innerHTML = `${data['status']}  ${parseFloat(data['percentage']).toFixed(2)}%`;
            } else if (data['status'] == 'Completed') {
                document.querySelector(`tr#${tr_id} td.status`).innerHTML = `${data['status']}`;
                document.querySelector(`tr#${tr_id} td.gen-time`).innerHTML = `${data['gen_time']}`;
                document.querySelector(`tr#${tr_id} td.result-file`).innerHTML = `<a href="${data['file_link']}">Download</a>`;
                $(`tr#${tr_id} td.status`).addClass('text-success');
            } else if (data['status'] == 'Failed') {
                console.log("failed");
                document.querySelector(`tr#${tr_id} td.status`).innerHTML = `${data['status']}`;
                document.querySelector(`tr#${tr_id} td.gen-time`).innerHTML = `${data['gen_time']}`;
                $(`tr#${tr_id} td.status`).addClass('text-danger');
            }
        }
    };
    poSocket.onclose = function(e) {
        console.error('Po socket closed unexpectedly');
    };
