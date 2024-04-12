% =======================================================
% Scripts to plot animation of satellite data for the
% Iceland Basin. 
%
%            Elisa Lovecchio (elisa.lovecchio@noc.ac.uk)
% =======================================================

clear all
clc

indir_main='C:\Users\ellove\Desktop\WORK\PARTITRICS\Satellite_data\';

sat_dir=[indir_main,'Sat_data\'];
ssh025_file=[sat_dir,'March-09Apr_cmems_obs-sl_glo_phy-ssh_nrt_allsat-l4-duacs-0.25deg_P1D_1712651501741.nc']; dayiniSSH=1;%25;
% Note that, if loading more than one file per product, data must cover THE SAME AREA
ssh0125_file1=[sat_dir,'March2024_cmems_obs-sl_eur_phy-ssh_nrt_allsat-l4-duacs-0.125deg_P1D_1712665949998.nc'];
ssh0125_file2=[sat_dir,'01-09Apr_cmems_obs-sl_eur_phy-ssh_nrt_allsat-l4-duacs-0.125deg_P1D_1712666222448.nc']; % https://doi.org/10.48670/moi-00142
SST_file=[sat_dir,'March_03Apr_IFREMER-GLOB-SST-L3-NRT-OBS_FULL_TIME_SERIE_1712653266426.nc']; dayiniSST=dayiniSSH;
CHL1kmL3_file1=[sat_dir,'March2024_cmems_obs-oc_atl_bgc-plankton_my_l3-multi-1km_P1D_1712656987689.nc'];
CHL1kmL3_file2=[sat_dir,'01-07Apr_cmems_obs-oc_atl_bgc-plankton_nrt_l3-multi-1km_P1D_1712657091865.nc'];
%CHL300mL3_file1=[sat_dir,'March-07Apr_cmems_obs-oc_glo_bgc-plankton_nrt_l3-olci-300m_P1D_1712654622171.nc'];
%CHL300mL3_file2=[sat_dir,'01-07Apr_cmems_obs-oc_atl_bgc-plankton_nrt_l3-olci-300m_P1D_1712651695401.nc'];

topo_file='C:\Users\ellove\Desktop\WORK\OBSdata\GEBCO_topo\GEBCO_IcelandBasin\gebco_2022_n70.0_s50.0_w-35.0_e0.0.nc';

% -------
doCHL300m=false; % do you have the data from the 300 m res OLCI sats?
zoom=true;
do_movmean=true; % moving mean to minimize cloud cover missing points? 
dmov=3; % moving mean window

invar_nickname300m='olci300mL3NRT';
invar_nickname1km='olci1kmL3MY';


% ========
% define tags and stuff

if zoom==false
    lim_var300m=[0,0.5];
    lim_var1km=[0,0.5];
    tagZ='';
    tagSSH='DUACS geostr U,V 25km';
else
    lim_var300m=[0,0.4];
    lim_var1km=[0,0.4];
    tagZ='ZOOM_';
    tagSSH='DUACS-EuroSeas geostr U,V 12km';
end

if do_movmean
    tagMovM='_MovMean';
    flagMovM='\fontsize{8} (movmean 3 days)';
else
    tagMovM='';
    flagMovM='';
end


%% Read in satellite data

disp('Reading in satellite data')

% -----------------------------------------


if doCHL300m

    disp('Reading in CHL 300m L3 from the satellites')

    CHL300m=ncread(CHL300mL3_file1,'CHL');
    %CHL300m=cat(3,CHL300m,ncread(CHL300mL3_file2,'CHL'));

    CHL300m_lat=ncread(CHL300mL3_file1,'latitude');
    CHL300m_lon=ncread(CHL300mL3_file1,'longitude');
    CHL300m_lon=repmat(CHL300m_lon,1,length(CHL300m_lat));
    CHL300m_lat=repmat(CHL300m_lat',length(CHL300m_lon),1);

    NT=size(CHL300m,3);
    tagCHL='300m';

else

    disp('Reading in CHL 1km L3 from the satellites')

    CHL1km=ncread(CHL1kmL3_file1,'CHL');
    CHL1km=cat(3,CHL1km,ncread(CHL1kmL3_file2,'CHL'));

    if do_movmean; CHL1km=movmean(CHL1km,dmov,3,"omitnan"); end

    CHL1km_lat=ncread(CHL1kmL3_file1,'latitude');
    CHL1km_lon=ncread(CHL1kmL3_file1,'longitude');
    CHL1km_lon=repmat(CHL1km_lon,1,length(CHL1km_lat));
    CHL1km_lat=repmat(CHL1km_lat',length(CHL1km_lon),1);

    NT=size(CHL1km,3);
    tagCHL='1km';

    % -----------------------------------------
end

% ------------------------------------------------

disp('Reading in SSH, U, V')

if zoom==false

    ssh=ncread(ssh025_file,'sla',[1,1,dayiniSSH],[inf,inf,inf]);
    uvel=ncread(ssh025_file,'ugos');
    vvel=ncread(ssh025_file,'vgos');%,[1,1,dayofint],[inf,inf,1]);
    ssh_lat=ncread(ssh025_file,'latitude');
    ssh_lon=ncread(ssh025_file,'longitude');

    ssh_lon=repmat(ssh_lon,1,length(ssh_lat));
    ssh_lat=repmat(ssh_lat',length(ssh_lon),1);

else % use higher resolution product

    ssh=ncread(ssh0125_file1,'sla');
    ssh=cat(3,ssh,ncread(ssh0125_file2,'sla'));
    uvel=ncread(ssh0125_file1,'ugos');
    uvel=cat(3,uvel,ncread(ssh0125_file2,'ugos'));
    vvel=ncread(ssh0125_file1,'vgos');%,[1,1,dayofint],[inf,inf,1]);
    vvel=cat(3,vvel,ncread(ssh0125_file2,'vgos'));

    ssh_lat=ncread(ssh0125_file1,'latitude');
    ssh_lon=ncread(ssh0125_file1,'longitude');

    ssh_lon=repmat(ssh_lon,1,length(ssh_lat));
    ssh_lat=repmat(ssh_lat',length(ssh_lon),1);

end



% ------------------------------------------------

disp('Reading in SST')

SST=ncread(SST_file,'adjusted_sea_surface_temperature',[1,1,dayiniSST],[inf,inf,inf])-273.15;%,[1,1,dayofint],[inf,inf,1])-273.15;
SST_lat=ncread(SST_file,'latitude');
SST_lon=ncread(SST_file,'longitude');

SST_lon=repmat(SST_lon,1,length(SST_lat));
SST_lat=repmat(SST_lat',length(SST_lon),1);

if do_movmean; SST=movmean(SST,dmov,3,"omitnan"); end

% ------------------------------------------------


disp('Reading in topography')

topo=ncread(topo_file,'elevation');
topo_lat=ncread(topo_file,'lat');
topo_lon=ncread(topo_file,'lon');

topo_nan=topo;
topo_nan(topo>=0)=NaN;
topo_lon=repmat(topo_lon,1,length(topo_lat));
topo_lat=repmat(topo_lat',length(topo_lon),1);

% reduce nr of data points
dX=5;
topo=topo(1:dX:end,1:dX:end);
topo_lon=topo_lon(1:dX:end,1:dX:end);
topo_lat=topo_lat(1:dX:end,1:dX:end);


% -------------------------------------------------




%% Locations of interest

depl_loc_lon=-24; 
depl_loc_lat=60;
depl_loc_label={'DL'};

lons_region=[-16.51,-16.47,-16.55];
lats_region=[48.84,48.67,49]; 
labels_sites={'C1','M43','C2'};



%% 2D plot of data on satellite data

disp('Plotting.....')

% Iceland Basin
if zoom
    dlon=4; dlat=3;
    latmin=depl_loc_lat-dlat; latmax=depl_loc_lat+dlat;
    lonmin=depl_loc_lon-dlon; lonmax=depl_loc_lon+dlon;
else
    latmin=55; latmax=64;
    lonmin=-30; lonmax=-12;
end
dLat=0.5; dLon=0.5;
m_proj('equi','lon',[lonmin,lonmax],'lat',[latmin,latmax]);

% topo colors
cmap=cmocean('deep',40)+0.2;
cmap(cmap>1)=1;
cmap=flipud(cmap(6:35,:));
lc=cmap(1,:);

% ssh colors
palette_path='C:\Users\ellove\Desktop\WORK\MATLAB\Palettes\';
load([palette_path,'DivergentEli.mat']);

% CHL colors
cmap_fluo=cmocean('speed',20);

% SST colors
cmap_sst=flipud(cbrewer2('RdYlBu',12));%20));

Ncol=20;
cmap_pCO2=cmocean('thermal',17);
lim_pCO2=[250,420];
pCO2_class=lim_pCO2(1);

lw=1;
dx=2;

a=8;
b=8;

ms=30; % marker size


%%

for dd=1:NT

    % date
    if dd<=31
        date=[num2str(dd,'%02.f'),'/March/2024'];
        date1=[num2str(dd,'%02.f'),'Mar23'];
    else
        date=[num2str(dd-31,'%02.f'),'/April/2024'];
        date1=[num2str(dd-31,'%02.f'),'/Apr23'];
    end
    % ----
    

    hf=figure(10);
    clf;
    hold on

    sgtitle([date,flagMovM]);

    % --------

    hsp1=subplot(1,2,1);
    hold on

    if doCHL300m

        title_string_CHL300m=['OLCI 300m L3 NRT CHL [mg m^{-3}] + ',tagSSH];
        title(title_string_CHL300m)

        m_pcolor(CHL300m_lon,CHL300m_lat,CHL300m(:,:,dd));
        shading flat;
        colormap(hsp1,cmap_fluo);
        clim(lim_var300m)
        cb1=colorbar;
        cb1.Limits=lim_var300m;
        cb1.Label.String='CHL [mg m^{-3}]';

        m_plot(depl_loc_lon,depl_loc_lat,'.r','MarkerSize',ms);
        ht=m_text(depl_loc_lon,depl_loc_lon,depl_loc_label);
        set(ht,'Color','r')

        m_contour(topo_lon,topo_lat,topo,[-1000 -2000],'Color',[0.3 0.3 0.3],'LineWidth',1);
        m_quiver(ssh_lon,ssh_lat,uvel(:,:,dd),vvel(:,:,dd),'k','AutoScaleFactor',2.5);

        m_contour(topo_lon,topo_lat,topo,[0 0],'Color','k','LineWidth',1.5);

        m_grid;

        hold off

    else

        title_string_CHL1km=['MULTI 1km L3 MY+NRT CHL [mg m^{-3}] + ',tagSSH]; % https://data.marine.copernicus.eu/product/OCEANCOLOUR_ATL_BGC_L4_NRT_009_116/description
        title(title_string_CHL1km)

        m_pcolor(CHL1km_lon,CHL1km_lat,CHL1km(:,:,dd));
        shading flat;
        colormap(cmap_fluo);
        clim(lim_var1km)
        cb1=colorbar;
        cb1.Limits=lim_var1km;
        cb1.Label.String='CHL [mg m^{-3}]';

        m_plot(depl_loc_lon,depl_loc_lat,'.r','MarkerSize',ms);
        ht=m_text(depl_loc_lon,depl_loc_lon,depl_loc_label);
        set(ht,'Color','r')

        m_contour(topo_lon,topo_lat,topo,[-1000 -2000],'Color',[0.3 0.3 0.3],'LineWidth',1);
        m_quiver(ssh_lon,ssh_lat,uvel(:,:,dd),vvel(:,:,dd),'k','AutoScaleFactor',2.5);

        m_contour(topo_lon,topo_lat,topo,[0 0],'Color','k','LineWidth',1.5);
        m_grid;

        hold off

    end

    % -----
if dd<35

    hsp2=subplot(1,2,2);

    hold on

    title(['ODYSSEA SST 10km-res Multi-sensor L3 + ',tagSSH])

    m_pcolor(SST_lon,SST_lat,SST(:,:,dd));
    shading flat;
    colormap(hsp2,cmap_sst);
    clim([7,13])
    cb1=colorbar;
    cb1.Label.String='SST [^{o}C]';

    m_plot(depl_loc_lon,depl_loc_lat,'.r','MarkerSize',ms);
    ht=m_text(depl_loc_lon,depl_loc_lon,depl_loc_label);
    set(ht,'Color','r')

    m_contour(topo_lon,topo_lat,topo,[-1000 -2000],'Color',[0.3 0.3 0.3],'LineWidth',1);
    m_quiver(ssh_lon,ssh_lat,uvel(:,:,dd),vvel(:,:,dd),'k','AutoScaleFactor',2.5);

    m_contour(topo_lon,topo_lat,topo,[0 0],'Color','k','LineWidth',1.5);

    m_grid;

    hold off

end

    % --------

    hold off 


    % == VIDEO

    filename=[indir_main,'Animations\',tagZ,'IcelandBasin_CHL',tagCHL,'NAtl_SST_March-07April2024',tagMovM];

    drawnow
    frame = getframe(10);
    %im = frame2im(frame);
    %[A,map] = rgb2ind(im,256);
    if dd == 1
        writerObj = VideoWriter(filename);
        writerObj.FrameRate = 1;
        open(writerObj);
        writeVideo(writerObj, frame);
        % imwrite(A,map,filename,'gif','LoopCount',inf,'DelayTime',0.2);
    else
        writeVideo(writerObj, frame);
        % imwrite(A,map,filename,'gif','WriteMode','append','DelayTime',0.2);
    end



end

close(writerObj)

disp('DONE.')