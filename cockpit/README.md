add: marmorata, taxifolia

i want to use the same cockpit approach as this project: how they have cockpit installed on system but use the containerized one for the web interface. this is desirable behavior.
should be configured through the chezmoi.yaml.tmpl single source of truth file. 
also make sure to include the caddy file so that i can check out the quadlet.
i want cockpit to have access to the other services (quadlets) that are on network, making it so that i can always check on the status of key services from this central dashboard. the cockpit associalted .tmpl file should therefore reflect the desired configuration in chezmoi.yaml.tmpl
