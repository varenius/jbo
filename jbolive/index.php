<!DOCTYPE html>
<html>
<head>
<meta http-equiv="refresh" content="5">
<style>
th {
    background-color: #4CAF50;
    color: black;
}
th, td {
    padding: 5px;
    text-align: center;
    vertical-align: center;
}
tr:nth-child(even) {background-color: #f2f2f2;}
</style>
</head>
<body>
<h1>JBO live telescope status (updates every 5 seconds)</h1>


<?php
function get_teldata($address = '127.0.0.1', $port=50000) {
    /* Create a TCP/IP socket. */
    $socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
    if ($socket === false) {
        echo "socket_create() failed: reason: " . 
             socket_strerror(socket_last_error()) . "\n";
    }
    
    $result = socket_connect($socket, $address, $port);
    if ($result === false) {
        echo "socket_connect() failed.\nReason: ($result) " . 
              socket_strerror(socket_last_error($socket)) . "\n";
    }
    
    # Request data for all telescopes
    $in = 'ALL';
    socket_write($socket, $in, strlen($in));

    # Receiver data for all telescopes
    $teldata = socket_read($socket, 131072);

    # Done, close socket
    socket_close($socket);
    return $teldata;
}
$td = get_teldata();
$obj = json_decode($td);
$tnames = array('42ft', '7metre', 'Lovell', 'Mark 2', 'Pickmere', 'Darnhall', 'Knockin', 'Defford', 'Cambridge');

function get_jobname($obj, $t) {
  if (!empty($obj->$t->status->jobname)) {
    $val = $obj->$t->status->jobname;
    return str_replace('_',' ',$val);
  }
  else {
    return '';
  }
}

function get_cel($obj, $t) {
  if (!empty($obj->$t->status->actual_azel)) {
    $val = round($obj->$t->status->actual_azel[1]*180.0/M_PI,2);
    return number_format($val,2) . '&deg';
  }
  else {
    return '';
  }
}

function get_caz($obj, $t) {
  if (!empty($obj->$t->status->actual_azel)) {
    $val = round($obj->$t->status->actual_azel[0]*180.0/M_PI,2);
    return number_format($val,2) . '&deg';
  }
  else {
    return '';
  }
}

function get_control($obj, $t) {
  if (!empty($obj->$t->status->control)) {
    return $obj->$t->status->control;
  }
  else {
    return '';
  }
}

function get_currentrec($obj, $t) {
  if (!empty($obj->$t->status->receiverstatus->currentrec)) {
    return $obj->$t->status->receiverstatus->currentrec;
  }
  else {
    return '';
  }
}

function get_cryotemp($obj, $t) {
  if (!empty($obj->$t->status->receiverstatus->currentreccryotemp)) {
    return $obj->$t->status->receiverstatus->currentreccryotemp . 'K';
  }
  else {
    return '';
  }
}

function get_timestamp($obj, $t) {
  if (!empty($obj->$t->status->time_isot)) {
    $isot = $obj->$t->status->time_isot;
    return str_replace('T',' ',$isot);
  }
  else {
    return '';
  }
}

?>
<div style="overflow-x:auto;">
<table>
  <thead>
    <tr>
      <td></td><?php foreach ($tnames as $tn) {echo '<th>' . $tn . '</th>'; }?>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>Control</th><?php foreach ($tnames as $tn) {echo '<td>' . get_control($obj, $tn) . '</td>'; }?>
    </tr>
    <tr>
      <th>Jobname</th><?php foreach ($tnames as $tn) {echo '<td>' . get_jobname($obj, $tn) . '</td>'; }?>
    </tr>
    <tr>
      <th>Azimuth</th><?php foreach ($tnames as $tn) {echo '<td>' . get_caz($obj, $tn) . '</td>'; }?>
    </tr>
    <tr>
      <th>Elevation</th><?php foreach ($tnames as $tn) {echo '<td>' . get_cel($obj, $tn) . '</td>'; }?>
    </tr>
    <tr>
      <th>Receiver</th><?php foreach ($tnames as $tn) {echo '<td>' . get_currentrec($obj, $tn) . '</td>'; }?>
    </tr>
    <tr>
      <th>Cryo temperature</th><?php foreach ($tnames as $tn) {echo '<td>' . get_cryotemp($obj, $tn) . '</td>'; }?>
    </tr>
    <tr>
      <th>HSL2 UTC timestamp</th><?php foreach ($tnames as $tn) {echo '<td>' . get_timestamp($obj, $tn) . '</td>'; }?>
    </tr>
  </tbody>
</table>
</div>
</body>
</html>
