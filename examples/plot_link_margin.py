from shannon.link_budget import LinkBudget

# Design a Low Earth Orbit (LEO) Downlink at 2.4 GHz
link = LinkBudget(frequency=2.4e9, distance_km=600)

# Add Components
link.set_transmitter(power_dbm=30, cable_loss=1, antenna_gain=0) # 1W Tx
link.add_path_loss(atmosphere_loss=0.5)
link.set_receiver(antenna_gain=15, noise_temp=150) # High gain ground yagi

link.calculate_margin(data_rate=9600, required_eb_no=10.0)
link.plot_waterfall()
