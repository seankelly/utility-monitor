## Power Monitoring with rtl-sdr

Inspired by a [blog post][kroy], I decided to set up power monitoring for myself too.
I however like the simple look of rrdtool so I am using that to store the data.

This uses [rtlamr][rtlamr] to process the radio broadcasts by the meter.
I live in a less dense location than the blog author so only picked up three meters using the `idm+` message.
My meter included a serial number on its face that directly matched one of those three meters so it was very easy to get the right reading.

### Running

Install rtl-sdr on the system that has the rtl-sdr device.
Install rtlamr rrdtool and its Python bindings on the system that will do the processing.
For me, I have it all on the same computer.

The `power/rtl_tcp_cron` script will run a tmux session with `rtl_tcp` in it.
Use one of two scripts to get the data into the rrdtool database.

* The `power/meter_reading.py` script will use `rtlamr`'s one-shot mode to connect and wait for a broadcast.
  I tried this for a while but had issues with `rtl_tcp` not working after some number of connections.
  This method works better if you need to use the rtl-sdr device for other things.
* The `power/rtlamr_sample` script maintains a single connection to `rtl_tcp` and writes each reading to a file.
  Use the `power/meter_reading.py` script with the `--input` option and that file to add the consumption amount from that reading to the database.

Finally, the `power/graph_usage` script will create four graphs:
* Today's usage.
* Yesterday's usage.
* This week's usage.
* This month's usage.
* Last month's usage (soon).

Each graph will contain the kWh consumed over that time period.

[kroy]: https://blog.kroy.io/monitoring-home-power-consumption-for-less-than-25/
[rtlamr]: https://github.com/bemasher/rtlamr
[rtl-sdr]: https://osmocom.org/projects/rtl-sdr/wiki/Rtl-sdr
