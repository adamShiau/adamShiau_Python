%clc
%clear all
%close all

%z=csvread('20191111-0001_0',num2str(i), '.csv',4,0);


%z2=csvread('20190426_CL_P_ETH_1.csv'); % P-EARTH
%z3=csvread('20190426_CL_N_ETH_1.csv'); % N-EARTH
%z=load('5hr.txt');

%figure(777)
%plot(z(:,1),z(:,2),z2(:,1),z2(:,2),z3(:,1),z3(:,2));

%data input
%{
data=0;
j=0;

for i=0:1:132,j=j+1000005,
    aaa=['D:\FOG test\SRS200\20200302_Allan\20200302_allan' ,num2str(i), '.csv'];
data=xlsread(aaa,1,'A1:B1000008');

Time(j-1000004:j,1)=data(:,1)+(i-4)*10000.04232586;
z_measured(j-1000004:j,1)=data(:,2);%.*1e1;


end

for i=10:1:22,j=j+1000005,
    aaa=['D:\Sparrow test\20191129allan\20191202-0001_' ,num2str(i), '.csv'];
data=xlsread(aaa,1,'A1:B1000008');

Time(j-1000004:j,1)=data(:,1)+(i-4)*10000.04232586;
z_measured(j-1000004:j,1)=data(:,2);%.*1e1;


end

%}
cd 'D:\FOG test\20201111_3allan';
z=readmatrix('20201111_SRS200.txt');  
z1=readmatrix('20201111_FOG1.txt');  
z2=readmatrix('20201111_FOG2.txt'); 
% i=0;
%  i=40:40:11028937;
%     datatrim(i,:)=[];
%  ans= (datatrim(:,2)-M)/-159.8;

%%
%SRS

TimeSRS=z(:,1);
RateSRS=z(:,2).*3600; %deg/s to deg/h
Fs=100*(TimeSRS(2,1)-TimeSRS(1,1)); % time unit in seconds.
TSRS=TimeSRS(:,1)./3600; %Time in hr
%omega_ori=z_measured(:,1);  


%omega = filter(1,1,RateSRS);

figure(9)
%plot(TSRS,omega_ori,'k',TSRS,RateSRS,'m'),xlabel('Time (hrs)'),ylabel('Output (deg/hr)')%,legend('Filter=1')
plot(TSRS,RateSRS,'m'),xlabel('Time (hrs)'),ylabel('Output (deg/hr)')%,legend('Filter=1')


t0 = Fs; % Allan fig time unit in seconds
theta = cumsum(RateSRS, 1)*t0;
maxNumM = 100;
L = size(theta, 1);
maxM = 2.^floor(log2(L/2));
m = logspace(log10(1), log10(maxM), maxNumM).';
m = ceil(m); % m must be an integer.
m = unique(m); % Remove duplicates.

tau = m*t0;  % Averaging time, m: averaging factor

avar = zeros(numel(m), 1);
for i = 1:numel(m)
    mi = m(i);
    avar(i,:) = sum( ...
        (theta(1+2*mi:L) - 2*theta(1+mi:L-mi) + theta(1:L-2*mi)).^2, 1);
end
avar = avar ./ (2*tau.^2 .* (L - 2*m)); % AVAR: Allan Variance


adev = sqrt(avar); % ADEV: Allan deviation

% figure
% loglog(tau, adev)
% title('Allan Deviation')
% xlabel('\tau');
% ylabel('\sigma(\tau)')
% grid on
%axis equal

%% Angle Random Walk, ARW 

% Find the index where the slope of the log-scaled Allan deviation is equal
% to the slope specified.
slope = -0.5;
logtau = log10(tau);
logadev = log10(adev);
dlogadev = diff(logadev) ./ diff(logtau);
[~, i] = min(abs(dlogadev - slope));

% Find the y-intercept of the line.
b = logadev(i) - slope*logtau(i);

% Determine the angle random walk coefficient from the line.
logN = slope*log(1) + b;
N = (10^logN);              

% ARW unit of deg/sqrt(hr)
%ARW_deg_rtHr=60*N

ARW_SRS200=N

% Plot the results.
 tauN = 1;
 lineN = N ./ sqrt(tau);


%% Rate Random Walk, RRW

% Find the index where the slope of the log-scaled Allan deviation is equal
% to the slope specified.
slope = 0.5;
logtau = log10(tau);
logadev = log10(adev);
dlogadev = diff(logadev) ./ diff(logtau);
[~, i] = min(abs(dlogadev - slope));

% Find the y-intercept of the line.
b = logadev(i) - slope*logtau(i);

% Determine the rate random walk coefficient from the line.
logK = slope*log10(3) + b;
K = 10^logK;
% RRW unit in deg/((hr)^1.5)
%Rate_RW=K*60*3600

RRW_SRS200=K

% Plot the results.
 tauK = 3;
 lineK = K .* sqrt(tau/3);


%% Bias Instability, BS
% Find the index where the slope of the log-scaled Allan deviation is equal
% to the slope specified.
slope = 0;
logtau = log10(tau);
logadev = log10(adev);
dlogadev = diff(logadev) ./ diff(logtau);
[~, i] = min(abs(dlogadev - slope));

% Find the y-intercept of the line.
b = logadev(i) - slope*logtau(i);

% Determine the bias instability coefficient from the line.
scfB = sqrt(2*log(2)/pi);
logB = b - log10(scfB);
B = 10^logB;

% Bias_ins unit of deg/hr

%Bias_instability_deg_hr=3600*B

BS_SRS200=B

% Plot the results.
 tauB = tau(i);
 lineB = B * scfB * ones(size(tau));
% figure
% loglog(tau, adev, tau, lineB, '--', tauB, scfB*B, 'o')
% title('Allan Deviation with Bias Instability')
% xlabel('\tau')
% ylabel('\sigma(\tau)')
% legend('\sigma', '\sigma_B')
% text(tauB, scfB*B, '0.664B')
% grid on
%axis equal


% %% Quantization Noise , QN 
% 
% % Find the index where the slope of the log-scaled Allan deviation is equal
% % to the slope specified.
% slope = -1;
% logtau = log10(tau);
% logadev = log10(adev);
% dlogadev = diff(logadev) ./ diff(logtau);
% [~, i] = min(abs(dlogadev - slope));
% 
% % Find the y-intercept of the line.
% b = logadev(i) - slope*logtau(i);
% 
% % Determine the QN coefficient from the line.
% logQ = slope*log(sqrt(3)) + b;
% Q = (10^logQ);              
% 
% % QN unit of 
% Quantum_Noise=Q
% 
% % Plot the results.
%  tauQ = sqrt(3);
%  lineQ = tauQ.*(Q ./ (tau));






tauParams = [tauN, tauK, tauB];
params = [N, K, scfB*B]; % 縱軸單位
figure
loglog(tau, adev, tau, [lineN, lineK, lineB], '--', ...
   tauParams, params, 'o')
title('Allan Deviation SRS200')
xlabel(' Averaging time, \tau, Seconds')
ylabel('Allan Deviation, \sigma(\tau), deg/hr')
legend('\sigma', '\sigma_N', '\sigma_K', '\sigma_B','location','southwest')
text(tauParams, params, {'N', 'K', '0.664B',})
grid on
%axis equal




% 
% tauParams = [tauN, tauK, tauB/3600];
% params = [60*N, 60*3600*K, 3600*scfB*B]; % 縱軸單位
% figure
% loglog(tau./3600, 3600*adev, tau./3600, 3600.*[lineN, lineK, lineB], '--', ...
%    tauParams, params, 'o')
% title('Allan Deviation with Noise Parameters')
% xlabel(' Averaging time, \tau, Hours')
% ylabel('Allan Deviation, \sigma(\tau), deg/hr')
% legend('\sigma', '\sigma_N', '\sigma_K', '\sigma_B','location','southwest')
% text(tauParams, params, {'N', 'K', '0.664B',})
% grid on
%axis equal


