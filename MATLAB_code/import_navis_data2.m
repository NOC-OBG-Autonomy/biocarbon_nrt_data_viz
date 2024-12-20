% import_navis_data.m

clear

home_folder = 'C:\Users\hanshil\Documents\GitHub\biocarbon_nrt_data_viz\';

fnames = {'navis_101','navis_102'};

for xx_fname = 1:length(fnames)

fname = fnames{xx_fname};
in_folder = [home_folder 'Data/navis/' fname '/raw/'];
csv_folder = [home_folder 'Data/navis/' fname '/csv_files/'];
cd(in_folder)

files = dir('*.msg');
ftab_all = table();
fbintab_all = table();
%%
for fix = 1:length(files)
    cd(in_folder)
    %%
    fname = files(fix).name;
    bufraw = fileread(fname);
    start_ix = strfind(bufraw,'pH: 720-10285')+15+49;
    if isempty(start_ix)
        start_ix = strfind(bufraw,'pH: 720-10290')+15+49;
    end
    end_ix = strfind(bufraw,'Resm')-1-53-53;
    if ~isempty(start_ix) && ~isempty(end_ix)
    date_startix = strfind(bufraw,'terminated: ')+16;
    date_str = bufraw(date_startix+[0:19]);
    ptime = datenum(date_str,'mmm dd HH:MM:SS YYYY');
    lon_startix = strfind(bufraw,'Fix:  ')+5; lon_startix = lon_startix(1);
    plon = str2double(bufraw(lon_startix+(0:8)));
    plat = str2double(bufraw(lon_startix+(9:17)));
    %%
    bindat_startix = strfind(bufraw,'(Park Sample)')+14;
    bindat_endix = find(bufraw=='#',1)-1;
    buf_bin = bufraw(bindat_startix:bindat_endix);
    buf_bin_eol_ixs = find(buf_bin == newline);
    buf_bin_line_start_ixs = [1 buf_bin_eol_ixs(1:end-1)+1];
    buf_bin_line_lengths = diff([0 buf_bin_eol_ixs]);
    buf_bin_reshaped = repmat(' ',length(buf_bin_eol_ixs),max(buf_bin_line_lengths));
    for lix = 1:length(buf_bin_eol_ixs)
        buf_bin_reshaped(lix,1:buf_bin_line_lengths(lix)) = ...
            buf_bin(buf_bin_line_start_ixs(lix):buf_bin_eol_ixs(lix));
    end
    buf_bin = buf_bin_reshaped;
%     buf_bin = reshape(buf_bin,111,[])';
%     bindat_endix = bindat_end
%%
    fbintab = table();
    bin_n = size(buf_bin,1);
    fbintab.mtime = repmat(ptime,bin_n,1);
    fbintab.pnum = repmat(fix,bin_n,1);
    fbintab.lat = repmat(plat,bin_n,1);
    fbintab.lon = repmat(plon,bin_n,1);
    for ii = 1:bin_n
        fbintab.pres(ii) = str2double(buf_bin(ii,1:9));
        fbintab.T(ii) = str2double(buf_bin(ii,11:18));
        fbintab.S(ii) = str2double(buf_bin(ii,19:25));
        fbintab.NO3(ii) = str2double(buf_bin(ii,26:31));
        fbintab.O2ph(ii) = str2double(buf_bin(ii,32:38));
        fbintab.O2tV(ii) = str2double(buf_bin(ii,39:47));
        fbintab.mcoms1(ii) = str2double(buf_bin(ii,49:54));
        fbintab.mcoms2(ii) = str2double(buf_bin(ii,55:61));
        fbintab.mcoms3(ii) = str2double(buf_bin(ii,62:68));
        fbintab.phVrs(ii) = str2double(buf_bin(ii,69:78));
        fbintab.phVk(ii) = str2double(buf_bin(ii,79:88));
        fbintab.phIb(ii) = str2double(buf_bin(ii,89:99));
        fbintab.phIk(ii) = str2double(buf_bin(ii,100:size(buf_bin,2)));
    end
    %%
    %fbintab = fbintab(end:-1:1,:);
    %mnames = {'mcoms1','mcoms2','mcoms3'};
    %for mix = 1:length(mnames)
    %    mname = mnames{mix};
    %    [fbintab.([mname '_baseline']), fbintab.([mname '_spikes'])] = separate_spikes_median(fbintab.(mname),5);
    %end
    
    %fbintab_all = [fbintab_all;fbintab];
%%
    buf_hex = bufraw(start_ix:end_ix);
%     buf(1:78)
%     buf(end-77:end)
    buf_hex_eol_ixs = find(buf_hex == newline);
    buf_hex_line_start_ixs = [1 buf_hex_eol_ixs(1:end-1)+1];
    buf_hex_line_lengths = diff([0 buf_hex_eol_ixs]);
    buf_hex_reshaped = repmat(' ',length(buf_hex_eol_ixs),max(buf_hex_line_lengths));
    for lix = 1:length(buf_hex_eol_ixs)
        buf_hex_reshaped(lix,1:buf_hex_line_lengths(lix)) = ...
            buf_hex(buf_hex_line_start_ixs(lix):buf_hex_eol_ixs(lix));
    end
    buf_hex = buf_hex_reshaped;

%     buf_hex = reshape(buf_hex,79,[])';
    ftab = table();
    ftab.mtime = repmat(ptime,size(buf_hex,1),1);
    ftab.pnum = repmat(fix,size(buf_hex,1),1);
    ftab.lat = repmat(plat,size(buf_hex,1),1);
    ftab.lon = repmat(plon,size(buf_hex,1),1);
    ftab.pres = hex2dec(buf_hex(:,1:4))/10;
    ftab.pres(ftab.pres>6000) = ftab.pres(ftab.pres>6000) - hex2dec('FFFF')/10;
    ftab.T = hex2dec(buf_hex(:,5:8))/1000;
    ftab.C = hex2dec(buf_hex(:,9:14));
    ftab.oxy1 = hex2dec(buf_hex(:,15:20));
    ftab.oxy2 = hex2dec(buf_hex(:,21:26));
    ftab.v1 = hex2dec(buf_hex(:,27:28));
    mcoms_count_offset = 500;
    ftab.mcoms1 = hex2dec(buf_hex(:,29:34))-mcoms_count_offset; ftab.mcoms1(ftab.mcoms1==(hex2dec('FFFFFF')-mcoms_count_offset)) = nan;
    ftab.mcoms2 = hex2dec(buf_hex(:,35:40))-mcoms_count_offset; ftab.mcoms2(ftab.mcoms2==(hex2dec('FFFFFF')-mcoms_count_offset)) = nan;
    ftab.mcoms3 = hex2dec(buf_hex(:,41:46))-mcoms_count_offset; ftab.mcoms3(ftab.mcoms3==(hex2dec('FFFFFF')-mcoms_count_offset)) = nan;
    ftab.FChl = (ftab.mcoms1-50)*2.006E-03;
    ftab.beta = (ftab.mcoms2-49)*3.524E-07;
    ftab.FDOM = (ftab.mcoms3-51)*6.619E-03;
%     ftab.beta = (ftab.mcoms3-49)*3.524E-07;
%     ftab.FDOM = (ftab.mcoms2-51)*6.619E-03;
    ftab.pH1 = hex2dec(buf_hex(:,47:48));
    ftab.pH2 = hex2dec(buf_hex(:,49:54));
    ftab.pH3 = hex2dec(buf_hex(:,55:56));
    mnames = {'mcoms1','mcoms2','mcoms3'};
    %for mix = 1:length(mnames)
    %    mname = mnames{mix};
    %    [ftab.([mname '_baseline']), ftab.([mname '_spikes'])] = separate_spikes_median(ftab.(mname),7);
    %end

    %ftab_all = [ftab_all;ftab];
% %%
%     figure(1);clf;hold on
%     plot(ftab.mcoms1,ftab.pres); axis ij
%     plot(ftab.mcoms2,ftab.pres); axis ij
%     plot(ftab.mcoms3,ftab.pres); axis ij
% %%
%     figure(2);clf;hold on
%     plot(ftab.OCR1,ftab.pres); axis ij
%     plot(ftab.OCR2,ftab.pres); axis ij
%     plot(ftab.OCR3,ftab.pres); axis ij
%     plot(ftab.OCR4,ftab.pres); axis ij
    ftab.mtime = datetime(ftab.mtime, 'Format', 'yyyy/MM/dd HH:mm:ss', 'ConvertFrom', 'datenum');
    cd(csv_folder)
    fname = fname(6:end-4); 
    writetable(ftab, fname)
    disp([fname ' saved ! (thanks Nathan and Hans for that awesome piece of work.)'])
    end
end
end
