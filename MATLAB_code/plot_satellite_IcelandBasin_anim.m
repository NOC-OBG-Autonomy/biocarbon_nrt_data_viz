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
%ssh025_file1=[sat_dir,'March2024_cmems_obs-sl_glo_phy-ssh_nrt_allsat-l4-duacs-0.25deg_P1D_1713264304792.nc']; 
ssh025_file1=[sat_dir,'Apr24_cmems_obs-sl_glo_phy-ssh_nrt_allsat-l4-duacs-0.25deg_P1D_1714481515513.nc']; 
ssh025_file2=[sat_dir,'01-07May_cmems_obs-sl_glo_phy-ssh_nrt_allsat-l4-duacs-0.25deg_P1D_1715101255233.nc']; 

% Note that, if loading more than one file per product, data must cover THE SAME AREA
%ssh0125_file1=[sat_dir,'March2024_cmems_obs-sl_eur_phy-ssh_nrt_allsat-l4-duacs-0.125deg_P1D_1713270054058.nc'];
ssh0125_file1=[sat_dir,'Apr2024_cmems_obs-sl_eur_phy-ssh_nrt_allsat-l4-duacs-0.125deg_P1D_1715102011827.nc']; % https://doi.org/10.48670/moi-00142
ssh0125_file2=[sat_dir,'01-07May_cmems_obs-sl_eur_phy-ssh_nrt_allsat-l4-duacs-0.125deg_P1D_1715101686608.nc'];
%ssh0125_file3=[sat_dir,'17-30Apr_cmems_obs-sl_eur_phy-ssh_nrt_allsat-l4-duacs-0.125deg_P1D_1714480315550.nc'];

%SST_file1=[sat_dir,'March2024_IFREMER-GLOB-SST-L3-NRT-OBS_FULL_TIME_SERIE_1713271161176.nc'];
SST_file1=[sat_dir,'Apr2024_IFREMER-GLOB-SST-L3-NRT-OBS_FULL_TIME_SERIE_1715102259131.nc']; 
SST_file2=[sat_dir,'01-06May_IFREMER-GLOB-SST-L3-NRT-OBS_FULL_TIME_SERIE_1715102607729.nc']; 

%CHL1kmL3_file1=[sat_dir,'March2024_cmems_obs-oc_atl_bgc-plankton_my_l3-multi-1km_P1D_1713264081719.nc'];
CHL1kmL3_file1=[sat_dir,'01-14Apr_cmems_obs-oc_atl_bgc-plankton_nrt_l3-multi-1km_P1D_1713263783614.nc'];
CHL1kmL3_file2=[sat_dir,'15-30Apr_cmems_obs-oc_atl_bgc-plankton_nrt_l3-multi-1km_P1D_1714736239472.nc'];
CHL1kmL3_file3=[sat_dir,'01-06May_cmems_obs-oc_atl_bgc-plankton_nrt_l3-multi-1km_P1D_1715102733185.nc'];

%HAP1kmL3_file2=[sat_dir,'13-29Apr_HAPTO_cmems_obs-oc_atl_bgc-plankton_nrt_l3-multi-1km_P1D_1714485360087.nc'];

PIC_dir=[sat_dir,'PIC\'];
PIC_str1=[PIC_dir,'AQUA_MODIS.2024'];
PIC_str2='.L3m.DAY.PIC.NRT.x_pic.nc';

%CHL300mL3_file1=[sat_dir,'March-07Apr_cmems_obs-oc_glo_bgc-plankton_nrt_l3-olci-300m_P1D_1712654622171.nc'];
%CHL300mL3_file2=[sat_dir,'01-07Apr_cmems_obs-oc_atl_bgc-plankton_nrt_l3-olci-300m_P1D_1712651695401.nc'];

SST_climatology=[sat_dir,'monthly_clim_2000-2020_cmems_obs-sst_glo_phy_my_l3s_P1D-m.nc']; 

topo_file='C:\Users\ellove\Desktop\WORK\OBSdata\GEBCO_topo\GEBCO_IcelandBasin\gebco_2022_n70.0_s50.0_w-35.0_e0.0.nc';

% -------
doCHL300m=false; % do you have the data from the 300 m res OLCI sats?
zoom=false;
do_movmean=true; % moving mean to minimize cloud cover missing points? 
dmov=3; % moving mean window
do_dSST=true;
plot_PIC=true;

invar_nickname300m='olci300mL3NRT';
invar_nickname1km='olci1kmL3MY';


% ========
% define tags and stuff

if zoom==false
    lim_var300m=[0,1];
    lim_var1km=[0,1];
    tagZ='';
    tagSSH='DUACS geostr U,V 25km';
else
    lim_var300m=[0,1];
    lim_var1km=[0,1];
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

tag_dSST='';
if do_dSST
    month_length_2024=[31,29,31,30,31,30,31,31,30,31,30,31];
    
    d0clim=sum(month_length_2024(1:3))+1; % 01 April
    tag_dSST='delta';
end


%% Read in satellite data

disp('Reading in satellite data')

% -----------------------------------------


if doCHL300m

    disp('Reading in CHL 300m L3 from the satellites')

    CHL300m=ncread(CHL300mL3_file1,'CHL');
    CHL300m=cat(3,CHL300m,ncread(CHL300mL3_file2,'CHL'));
    CHL300m=cat(3,CHL300m,ncread(CHL300mL3_file3,'CHL'));

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
    CHL1km=cat(3,CHL1km,ncread(CHL1kmL3_file3,'CHL'));

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

    ssh=ncread(ssh025_file1,'sla');
    ssh=cat(3,ssh,ncread(ssh025_file2,'sla'));
    uvel=ncread(ssh025_file1,'ugos');
    uvel=cat(3,uvel,ncread(ssh025_file2,'ugos'));
    vvel=ncread(ssh025_file1,'vgos');%,[1,1,dayofint],[inf,inf,1]);
    vvel=cat(3,vvel,ncread(ssh025_file2,'vgos'));

    ssh_lat=ncread(ssh025_file1,'latitude');
    ssh_lon=ncread(ssh025_file1,'longitude');

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

SST=ncread(SST_file1,'adjusted_sea_surface_temperature')-273.15;
SST=cat(3,SST, ncread(SST_file2,'adjusted_sea_surface_temperature')-273.15 );

SST_lat=ncread(SST_file1,'latitude');
SST_lon=ncread(SST_file1,'longitude');
NX_SST=length(SST_lon);
NY_SST=length(SST_lat);

SST_lon=repmat(SST_lon,1,length(SST_lat));
SST_lat=repmat(SST_lat',length(SST_lon),1);

if do_movmean; SST=movmean(SST,dmov,3,"omitnan"); end



% ------------------------------------------------

if do_dSST

disp('Reading in SST climatology')

SST_clim=ncread(SST_climatology,'SST_clim');

month_ini_leap=0;
for mm=1:11
    month_ini_leap=[month_ini_leap,sum(month_length_2024(1:mm))];
end

SST_clim_interp=nan(NX_SST,NY_SST,366);
for mm=1:12
    middleday=month_ini_leap(mm)+fix(month_length_2024(mm)/2);
    SST_clim_interp(:,:,middleday)=SST_clim(:,:,mm);
end

SST_clim_interp=fillmissing(SST_clim_interp,'linear',3);

end

% ------------------------------------------------


if plot_PIC

    file1=[indir_main,'Sat_data\PIC\AQUA_MODIS.20240401.L3m.DAY.PIC.NRT.x_pic.nc'];

    PIC_lat=ncread(file1,'lat');
    PIC_lon=ncread(file1,'lon');
    NX_PIC=length(PIC_lon);
    NY_PIC=length(PIC_lat);

    PIC_lon=repmat(PIC_lon,1,length(PIC_lat));
    PIC_lat=repmat(PIC_lat',length(PIC_lon),1);


    PIC=[];
    for dd=1:NT
        if dd<31; mm='04'; md=dd; else; mm='05'; md=dd-30; end 
        PIC_today_file=[PIC_str1,mm,num2str(md,'%02.f'),PIC_str2];
        PIC_today=ncread(PIC_today_file,'pic');
        PIC=cat(3,PIC,PIC_today);
    end

    if do_movmean; PIC=movmean(PIC,dmov,3,"omitnan"); end

end


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
cmap_delta=divergent;

% CHL colors
cmap_fluo=cmocean('speed',20);

% SST colors
cmap_sst=flipud(cbrewer2('RdYlBu',12));%20));

% Haptophytes colour
cmap_hapto=cmocean('dense',20);

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

t0=1;

for dd=t0:NT

    % % date
    % if dd<=31
    %     date=[num2str(dd,'%02.f'),'/March/2024'];
    %     date1=[num2str(dd,'%02.f'),'Mar23'];
    % else
    %     date=[num2str(dd-31,'%02.f'),'/April/2024'];
    %     date1=[num2str(dd-31,'%02.f'),'/Apr23'];
    % end
    % ----

    if dd<31
        date=[num2str(dd,'%02.f'),'/April/2024'];
    else
        date=[num2str(dd-30,'%02.f'),'/May/2024'];
    end
    

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
%if dd<35




    hsp2=subplot(1,2,2);

    hold on


    if plot_PIC

        title(['AQUA-MODIS 4km L3 PIC Calcite [mmol m^{-3}] + ',tagSSH])

        m_pcolor(PIC_lon,PIC_lat,PIC(:,:,dd)*1000);
        shading flat;
        colormap(hsp2,cmap_hapto);
        clim([0,0.5])
        cb1=colorbar;
        cb1.Label.String='PIC [mmol m^{-3}]';


    else


        if do_dSST

            title({'\Delta SST: ODYSSEA SST 10km-res Multi-sensor L3 (ref mean 2000-2020) + ',tagSSH})

            m_pcolor(SST_lon,SST_lat,SST(:,:,dd)-SST_clim_interp(:,:,dd+d0clim));
            shading flat;
            colormap(hsp2,cmap_delta);
            clim([-2,2])
            cb1=colorbar;
            cb1.Label.String='\Delta SST [^{o}C]';


        else

            title(['ODYSSEA SST 10km-res Multi-sensor L3 + ',tagSSH])

            m_pcolor(SST_lon,SST_lat,SST(:,:,dd));
            shading flat;
            colormap(hsp2,cmap_sst);
            clim([7,13])
            cb1=colorbar;
            cb1.Label.String='SST [^{o}C]';

        end


    end % plot_hapto

    m_plot(depl_loc_lon,depl_loc_lat,'.r','MarkerSize',ms);
    ht=m_text(depl_loc_lon,depl_loc_lon,depl_loc_label);
    set(ht,'Color','r')

    m_contour(topo_lon,topo_lat,topo,[-1000 -2000],'Color',[0.3 0.3 0.3],'LineWidth',1);
    m_quiver(ssh_lon,ssh_lat,uvel(:,:,dd),vvel(:,:,dd),'k','AutoScaleFactor',2.5);

    m_contour(topo_lon,topo_lat,topo,[0 0],'Color','k','LineWidth',1.5);

    m_grid;

    hold off

    %end

    % --------

    hold off


    % == VIDEO

    if plot_PIC
        filename=[indir_main,'Animations\',tagZ,'IcelandBasin_CHL-PIC',tagCHL,'NAtl_April-06May2024',tagMovM];
    else
        filename=[indir_main,'Animations\',tagZ,'IcelandBasin_CHL',tagCHL,'NAtl_',tag_dSST,'SST_April-06May2024',tagMovM];
    end

    drawnow
    frame = getframe(10);
    %im = frame2im(frame);
    %[A,map] = rgb2ind(im,256);
    if dd == t0
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