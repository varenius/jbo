<?php $refresh_seconds = 30;?>
<!DOCTYPE html>
<html>
<head>
<meta http-equiv="refresh" content="<?php echo $refresh_seconds;?>">
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
		socket_strerror(socket_last_error($socket)) .
		". Are you sure hsl2receiver.py is running?";
    }
    
    # Request data for all telescopes
    $in = 'ALL';
    socket_write($socket, $in, strlen($in));

    # Receiver data for all telescopes
    $teldata = socket_read($socket, 131072);
    $teldata = substr($teldata, 3, strlen($teldata)-6);

    # Done, close socket
    socket_close($socket);
    #echo var_dump($teldata);
    return $teldata;
}
$td = get_teldata();
$obj = json_decode($td);
$tnames = array('42ft', '7metre', 'Lovell', 'Mark 2', 'Pickmere', 'Darnhall', 'Knockin', 'Defford', 'Cambridge');
$timages = array('42ft.jpg', '7m.jpg','lo.jpg', 'mk2.jpg', 'pi.jpg', 'da.jpg', 'kn.jpg', 'de.jpg', 'cm.jpg');
$diameters = array('13 m', '7 m', '76 m','38x25 m', '25 m', '25 m', '25 m', '25 m', '32 m');

function get_jobname($obj, $t) {
  if (!empty($obj->$t->status->jobname)) {
    $val = $obj->$t->status->jobname;
    return str_replace('_',' ',$val);
  }
  else {
    return '';
  }
}

function get_coord($obj, $t) {
  if (!empty($obj->$t->status->demanded_lonlat)) {
    return $obj->$t->status->demanded_lonlat[2];
  }
  else {
    return '';
  }
}

function get_RA($obj, $t) {
  if (!empty($obj->$t->status->demanded_lonlat)) {
    $val = $obj->$t->status->demanded_lonlat[0]*12.0/M_PI;
    $h = floor($val);
    $m= floor(($val-$h)*60);
    $s= round(($val-$h-$m/60)*3600,3);
    return  str_pad($h, 2, "0", STR_PAD_LEFT) . 'h' . str_pad($m, 2, "0", STR_PAD_LEFT) .  "m" . str_pad($s, 2, "0", STR_PAD_LEFT) . "s";
  }
  else {
    return '';
  }
}

function get_Dec($obj, $t) {
  if (!empty($obj->$t->status->demanded_lonlat)) {
    $val = $obj->$t->status->demanded_lonlat[1]*180.0/M_PI;
    $sign = $val <=> 0;
    $aval = abs($val);
    $deg = floor($aval);
    $amin= floor(($aval-$deg)*60);
    $asec= round(($aval-$deg-$amin/60)*3600,2);
    return  str_pad($sign*$deg, 2, "0", STR_PAD_LEFT) . '&deg' .str_pad($amin, 2, "0", STR_PAD_LEFT) .  "'" . str_pad($asec, 2, "0", STR_PAD_LEFT) . "''";
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
  $beg = '<td>';
  $val = '';
  $end = '</td>';
  if (!empty($obj->$t->status->control)) {
    $val = $obj->$t->status->control;
    if ($val == 'Observing_room') {
      $beg = "<td style='background-color: #49FFFF;'>";
    }
    elseif ($val == 'eMerlin') {
      $beg = "<td style='background-color: #AAA8FF;'>";
    }
    elseif ($val == 'Control_Room') {
      $beg = "<td style='background-color: #4BFF48;'>";
    }
    elseif ($val == 'VLBI') {
      $beg = "<td style='background-color: #FFFF60;'>";
    }
    elseif ($val == 'Test') {
      $beg = "<td style='background-color: #FFFFA6;'>";
    }
  }
  return $beg . str_replace('_',' ',$val) . $end;
}

function get_currentrec($obj, $t) {
  $beg = '<td>';
  $val = '';
  $end = '</td>';
  if (!empty($obj->$t->status->receiverstatus->currentrec)) {
    $val = $obj->$t->status->receiverstatus->currentrec;
      //if (strpos($val, 'L') !== false) {
      //  $beg = "<td style='background-color: #BDBDBD;'>";
      //}
      if (strpos($t, 'Defford') !== false) {
        if (($obj->$t->status->offsets_azel[1]*180.0/M_PI)>-1.0) {
          $val = "C-Band";
	}
      }
  }
  return $beg . $val . $end;
}

function get_cryotemp($obj, $t) {
  if (!empty($obj->$t->status->receiverstatus->currentreccryotemp)) {
    return $obj->$t->status->receiverstatus->currentreccryotemp . 'K';
  }
  else {
    return '';
  }
}

//echo var_dump($obj->Cambridge->status->receiverstatus->recstatuses[0]->LOs[0]->loidfreq);

function get_azoffset($obj, $t) {
  if (!empty($obj->$t->status->offsets_azel)) {
    $val = round($obj->$t->status->offsets_azel[0]*180.0/M_PI,3);
    return number_format($val,3) . '&deg';
  }
  else {
    return '';
  }
}

function get_eloffset($obj, $t) {
  if (!empty($obj->$t->status->offsets_azel)) {
    $val = round($obj->$t->status->offsets_azel[1]*180.0/M_PI,3);
    return number_format($val,3) . '&deg';
  }
  else {
    return '';
  }
}

function get_lok($obj, $t, $k) {
  $lo = ''; 
  if (!empty($obj->$t->status->receiverstatus->currentLOs)) {
    $CLOs = $obj->$t->status->receiverstatus->currentLOs;
    // Check if more than 4 LOs in current setup. If so, we have K-band
    // where LO[0] is the fixed 17GHz LO, so skip that and offset k-value 
    // by 1 to read the variable LOs instead also at K-band.
    if(count($CLOs)>4) { $k=$k+1; }
    $lo=$CLOs[$k-1]->loidfreq/1e6 . ' MHz';
  }
  return $lo;
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
      <td><h2>JBO live status<h2></td><?php foreach ($timages as $ti) {echo "<td> <img src='images/" . $ti . "' width='100%' ></td>"; }?>
    </tr>
    <tr>
    <tr>
      <td></td><?php foreach ($tnames as $tn) {echo '<th>' . $tn . '</th>'; }?>

    </tr>
    <tr>
      <th>Diameter</th><?php foreach ($diameters as $td) {echo '<td>' . $td . '</td>'; }?>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>Control</th><?php foreach ($tnames as $tn) {echo get_control($obj, $tn) ; }?>
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
      <th>Az. offset</th><?php foreach ($tnames as $tn) {echo '<td>' . get_azoffset($obj, $tn) . '</td>'; }?>
    </tr>
    <tr>
      <th>El. offset</th><?php foreach ($tnames as $tn) {echo '<td>' . get_eloffset($obj, $tn) . '</td>'; }?>
    </tr>
    <tr>
      <th>Coordinate system </th><?php foreach ($tnames as $tn) {echo '<td>' . get_coord($obj, $tn) . '</td>'; }?>
    </tr>
    <tr>
      <th>R.A. / Long. </th><?php foreach ($tnames as $tn) {echo '<td>' . get_RA($obj, $tn) . '</td>'; }?>
    </tr>
    <tr>
      <th>Dec. / Lat. </th><?php foreach ($tnames as $tn) {echo '<td>' . get_Dec($obj, $tn) . '</td>'; }?>
    </tr>
    <tr>
      <th>Receiver</th><?php foreach ($tnames as $tn) {echo get_currentrec($obj, $tn) ; }?>
    </tr>
    <tr>
      <th>Agilent LO</th><?php foreach ($tnames as $tn) {echo '<td>' . get_lok($obj, $tn, 1) . '</td>'; }?>
    </tr>
    <tr>
      <th>MERLIN LO</th><?php foreach ($tnames as $tn) {echo '<td>' . get_lok($obj, $tn, 2) . '</td>'; }?>
    </tr>
    <!-- <tr>
     <th>Cryo temperature</th><?php foreach ($tnames as $tn) {echo '<td>' . get_cryotemp($obj, $tn) . '</td>'; }?>
    </tr>-->
    <tr>
      <th>HSL2 UTC timestamp</th><?php foreach ($tnames as $tn) {echo '<td>' . get_timestamp($obj, $tn) . '</td>'; }?>
    </tr>
  </tbody>
</table>
</div>
</br>
NOTE: This information is for the use of Jodrell Bank Observatory staff in our
astronomy and engineering applications. We cannot guarantee the accuracy of the
data or fitness for use for any other purposes. The page refreshes
every <?php echo  $refresh_seconds;?>s. 
</body>
</html>
