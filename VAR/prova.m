%importing data
Trump = readtable('/Users/riccardodalcero/Library/CloudStorage/OneDrive-UniversitaCattolicaSacroCuore-ICATT/Materials/RA/Data/5_TrumpwithCohmetrix.csv');


% Convert the string column to datetime
Trump.DateTime = datetime(Trump.DateTime, 'InputFormat', 'yyyy-MM-dd HH:mm:ssXX','TimeZone','UTC');
Trump(1,:) = []; %eliminate the first rows containing the title 

%setting as time index
Trump = table2timetable(Trump, 'RowTimes', 'DateTime');

% Assuming X and DateTime are already defined

X = Trump.SYNLE;

% Convert DateTime to a datetime array
DateTime = datetime(Trump.DateTime.Year, Trump.DateTime.Month, Trump.DateTime.Day);

% Define the start and end dates for each week
startWeek = min(DateTime):7:max(DateTime);
endWeek = startWeek + days(6);

% Initialize arrays to store weekly averages and corresponding dates
weeklyAverages = zeros(size(startWeek));
weeklyDates = datetime(startWeek);

% Calculate weekly averages
for i = 1:numel(startWeek)
    % Find indices of observations within the current week
    weekIndices = DateTime >= startWeek(i) & DateTime <= endWeek(i);
    
    % Calculate the average of X within the current week
    weeklyAverages(i) = mean(X(weekIndices));
end
X_weekly = weeklyAverages ;
% Display the weekly averages and corresponding dates
disp("Weekly Averages:");
disp(weeklyAverages);
disp("Dates:");
disp(weeklyDates);
plot(weeklyDates,weeklyAverages)

Y = Trump.sentiment_score;

for i = 1:numel(startWeek)
    % Find indices of observations within the current week
    weekIndices = DateTime >= startWeek(i) & DateTime <= endWeek(i);
    
    % Calculate the average of X within the current week
    weeklyAverages(i) = mean(Y(weekIndices));
end
Y_weekly = weeklyAverages ;

Z = Trump.UI;

for i = 1:numel(startWeek)
    % Find indices of observations within the current week
    weekIndices = DateTime >= startWeek(i) & DateTime <= endWeek(i);
    
    % Calculate the average of X within the current week
    weeklyAverages(i) = mean(Z(weekIndices));
end
Z_weekly = weeklyAverages ;
Z = timetable(X_weekly', Y_weekly',Z_weekly', 'RowTimes', weeklyDates');

Z.Properties.VariableNames(3) = "EPU";
Z.Properties.VariableNames(2) = "Sent";
Z.Properties.VariableNames(1) = "SYN";

xlswrite("output.csv",[Z.EPU,Z.SYN,Z.Sent])