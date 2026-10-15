function out = model
%
% pc.m
%
% Model exported on Oct 15 2026, 16:31 by COMSOL 6.3.0.290.

import com.comsol.model.*
import com.comsol.model.util.*

model = ModelUtil.create('Model');

model.modelPath('H:\Optimize\phononic\PDCHA\code');


model.label('pc.mph');

model.param.set('a', '0.05[m]');
model.param.set('kx', 'if(k<1,(1-k)*pi/a,if(k<2,(k-1)*pi/a,pi/a))');
model.param.set('ky', 'if(k<1,(1-k)*pi/a,if(k<2,0,(k-2)*pi/a))');
model.param.set('N', '41');
model.param.set('k', '0');

model.component.create('comp1', true);

model.component('comp1').geom.create('geom1', 2);

model.result.table.create('tbl1', 'Table');
model.result.evaluationGroup.create('std1EvgFrq', 'EvaluationGroup');
model.result.evaluationGroup.create('std1mpf1', 'EvaluationGroup');
model.result.evaluationGroup('std1EvgFrq').create('gev1', 'EvalGlobal');
model.result.evaluationGroup('std1mpf1').create('gev1', 'EvalGlobal');

model.component('comp1').mesh.create('mesh1');

model.component('comp1').geom('geom1').create('pol1', 'Polygon');
model.component('comp1').geom('geom1').feature('pol1').set('source', 'file');
model.component('comp1').geom('geom1').feature('pol1').set('filename', 'C:\Users\Administrator\Desktop\article\test1\code\test\test_parametric_curve.txt');
model.component('comp1').geom('geom1').feature('pol1').set('selresult', true);
model.component('comp1').geom('geom1').create('r1', 'Rectangle');
model.component('comp1').geom('geom1').feature('r1').set('size', {'a' 'a'});
model.component('comp1').geom('geom1').feature('r1').set('base', 'center');
model.component('comp1').geom('geom1').create('dif1', 'Difference');
model.component('comp1').geom('geom1').feature('dif1').set('keepsubtract', true);
model.component('comp1').geom('geom1').feature('dif1').selection('input').set({'r1'});
model.component('comp1').geom('geom1').feature('dif1').selection('input2').set({'pol1'});
model.component('comp1').geom('geom1').create('igv2', 'IgnoreVertices');
model.component('comp1').geom('geom1').feature('igv2').selection('input').named('pol1');
model.component('comp1').geom('geom1').run;
model.component('comp1').geom('geom1').run('dif1');

model.component('comp1').material.create('mat3', 'Common');
model.component('comp1').material.create('mat4', 'Common');
model.component('comp1').material('mat3').selection.set([1]);
model.component('comp1').material('mat4').selection.set([2]);

model.component('comp1').common.create('mpf1', 'ParticipationFactors');

model.component('comp1').physics.create('solid', 'SolidMechanics', 'geom1');
model.component('comp1').physics('solid').create('pc1', 'PeriodicCondition', 1);
model.component('comp1').physics('solid').feature('pc1').selection.set([1 6]);
model.component('comp1').physics('solid').create('pc2', 'PeriodicCondition', 1);
model.component('comp1').physics('solid').feature('pc2').selection.set([2 3]);

model.result.table('tbl1').comments([native2unicode(hex2dec({'51' '68'}), 'unicode')  native2unicode(hex2dec({'5c' '40'}), 'unicode')  native2unicode(hex2dec({'8b' 'a1'}), 'unicode')  native2unicode(hex2dec({'7b' '97'}), 'unicode') ' 1']);

model.component('comp1').view('view1').axis.set('xmin', -0.05976683273911476);
model.component('comp1').view('view1').axis.set('xmax', 0.05976683273911476);
model.component('comp1').view('view1').axis.set('ymin', -0.03219666704535484);
model.component('comp1').view('view1').axis.set('ymax', 0.03219666704535484);

model.component('comp1').material('mat3').label([native2unicode(hex2dec({'78' '6c'}), 'unicode')  native2unicode(hex2dec({'67' '50'}), 'unicode')  native2unicode(hex2dec({'65' '99'}), 'unicode') ]);
model.component('comp1').material('mat3').propertyGroup('def').set('density', '1050');
model.component('comp1').material('mat3').propertyGroup('def').set('youngsmodulus', '3e5');
model.component('comp1').material('mat3').propertyGroup('def').set('poissonsratio', '0.49');
model.component('comp1').material('mat4').label([native2unicode(hex2dec({'8f' '6f'}), 'unicode')  native2unicode(hex2dec({'67' '50'}), 'unicode')  native2unicode(hex2dec({'65' '99'}), 'unicode') ]);
model.component('comp1').material('mat4').propertyGroup('def').set('density', '7850');
model.component('comp1').material('mat4').propertyGroup('def').set('youngsmodulus', '2.1e10');
model.component('comp1').material('mat4').propertyGroup('def').set('poissonsratio', '0.3');

model.component('comp1').physics('solid').feature('pc1').set('PeriodicType', 'Floquet');
model.component('comp1').physics('solid').feature('pc1').set('kFloquet', {'kx'; 'ky'; '0'});
model.component('comp1').physics('solid').feature('pc1').label(['kx_' native2unicode(hex2dec({'54' '68'}), 'unicode')  native2unicode(hex2dec({'67' '1f'}), 'unicode')  native2unicode(hex2dec({'60' '27'}), 'unicode')  native2unicode(hex2dec({'67' '61'}), 'unicode')  native2unicode(hex2dec({'4e' 'f6'}), 'unicode') ]);
model.component('comp1').physics('solid').feature('pc2').set('PeriodicType', 'Floquet');
model.component('comp1').physics('solid').feature('pc2').set('kFloquet', {'kx'; 'ky'; '0'});
model.component('comp1').physics('solid').feature('pc2').label(['ky_' native2unicode(hex2dec({'54' '68'}), 'unicode')  native2unicode(hex2dec({'67' '1f'}), 'unicode')  native2unicode(hex2dec({'60' '27'}), 'unicode')  native2unicode(hex2dec({'67' '61'}), 'unicode')  native2unicode(hex2dec({'4e' 'f6'}), 'unicode') ]);

model.study.create('std1');
model.study('std1').create('param', 'Parametric');
model.study('std1').create('eig', 'Eigenfrequency');
model.study('std1').feature('eig').set('geometricNonlinearity', true);

model.batch.create('p1', 'Parametric');
model.batch('p1').create('so1', 'Solutionseq');
model.batch('p1').study('std1');

model.sol.create('sol1');
model.sol('sol1').attach('std1');
model.sol.create('sol2');
model.sol('sol2').study('std1');
model.sol('sol2').label([native2unicode(hex2dec({'53' 'c2'}), 'unicode')  native2unicode(hex2dec({'65' '70'}), 'unicode')  native2unicode(hex2dec({'53' '16'}), 'unicode')  native2unicode(hex2dec({'89' 'e3'}), 'unicode') ' 1']);

model.result.numerical.create('gev1', 'EvalGlobal');
model.result.numerical('gev1').set('data', 'dset2');
model.result.create('pg1', 'PlotGroup2D');
model.result.create('pg2', 'PlotGroup1D');
model.result('pg1').set('data', 'dset2');
model.result('pg1').create('surf1', 'Surface');
model.result('pg1').feature('surf1').create('def', 'Deform');
model.result('pg2').set('data', 'dset2');
model.result('pg2').create('glob1', 'Global');
model.result('pg2').feature('glob1').set('data', 'dset2');
model.result('pg2').feature('glob1').set('expr', {'solid.freq'});

model.study('std1').feature('param').set('pname', {'k'});
model.study('std1').feature('param').set('plistarr', {'range(0,3/(N-1),3)'});
model.study('std1').feature('param').set('punit', {''});
model.study('std1').feature('eig').set('neigs', 8);
model.study('std1').feature('eig').set('neigsactive', true);
model.study('std1').feature('eig').set('filtereigdescription', {'Damped' 'natural' 'frequency'});

model.batch('p1').set('pname', {'k'});
model.batch('p1').set('plistarr', {'range(0,3/(N-1),3)'});
model.batch('p1').set('punit', {''});
model.batch('p1').set('err', true);
model.batch('p1').feature('so1').set('seq', 'sol1');
model.batch('p1').feature('so1').set('store', true);
model.batch('p1').feature('so1').set('psol', 'sol2');
model.batch('p1').feature('so1').set('keeprom', true);
model.batch('p1').feature('so1').set('param', {'"k","0"' '"k","0.075"' '"k","0.15"' '"k","0.225"' '"k","0.3"' '"k","0.375"' '"k","0.45"' '"k","0.525"' '"k","0.6"' '"k","0.675"'  ...
'"k","0.75"' '"k","0.825"' '"k","0.9"' '"k","0.975"' '"k","1.05"' '"k","1.125"' '"k","1.2"' '"k","1.275"' '"k","1.35"' '"k","1.425"'  ...
'"k","1.5"' '"k","1.575"' '"k","1.65"' '"k","1.725"' '"k","1.8"' '"k","1.875"' '"k","1.95"' '"k","2.025"' '"k","2.1"' '"k","2.175"'  ...
'"k","2.25"' '"k","2.325"' '"k","2.4"' '"k","2.475"' '"k","2.55"' '"k","2.625"' '"k","2.7"' '"k","2.775"' '"k","2.85"' '"k","2.925"'  ...
'"k","3"'});
model.batch('p1').attach('std1');

model.sol('sol1').createAutoSequence('std1');

model.study('std1').runNoGen;

model.result.dataset('dset1').set('frametype', 'spatial');
model.result.dataset('dset2').set('frametype', 'spatial');
model.result.numerical('gev1').label('fre_caculate');
model.result.numerical('gev1').set('table', 'tbl1');
model.result.numerical('gev1').set('tablecols', 'outer');
model.result.numerical('gev1').set('expr', {'solid.freq'});
model.result.numerical('gev1').set('unit', {'Hz'});
model.result.numerical('gev1').set('descr', {[native2unicode(hex2dec({'98' '91'}), 'unicode')  native2unicode(hex2dec({'73' '87'}), 'unicode') ]});
model.result.numerical('gev1').set('const', {'solid.refpntx' '0' [native2unicode(hex2dec({'52' '9b'}), 'unicode')  native2unicode(hex2dec({'77' 'e9'}), 'unicode')  native2unicode(hex2dec({'8b' 'a1'}), 'unicode')  native2unicode(hex2dec({'7b' '97'}), 'unicode')  native2unicode(hex2dec({'53' 'c2'}), 'unicode')  native2unicode(hex2dec({'80' '03'}), 'unicode')  native2unicode(hex2dec({'70' 'b9'}), 'unicode')  native2unicode(hex2dec({'ff' '0c'}), 'unicode') 'x ' native2unicode(hex2dec({'57' '50'}), 'unicode')  native2unicode(hex2dec({'68' '07'}), 'unicode') ]; 'solid.refpnty' '0' [native2unicode(hex2dec({'52' '9b'}), 'unicode')  native2unicode(hex2dec({'77' 'e9'}), 'unicode')  native2unicode(hex2dec({'8b' 'a1'}), 'unicode')  native2unicode(hex2dec({'7b' '97'}), 'unicode')  native2unicode(hex2dec({'53' 'c2'}), 'unicode')  native2unicode(hex2dec({'80' '03'}), 'unicode')  native2unicode(hex2dec({'70' 'b9'}), 'unicode')  native2unicode(hex2dec({'ff' '0c'}), 'unicode') 'y ' native2unicode(hex2dec({'57' '50'}), 'unicode')  native2unicode(hex2dec({'68' '07'}), 'unicode') ]; 'solid.refpntz' '0' [native2unicode(hex2dec({'52' '9b'}), 'unicode')  native2unicode(hex2dec({'77' 'e9'}), 'unicode')  native2unicode(hex2dec({'8b' 'a1'}), 'unicode')  native2unicode(hex2dec({'7b' '97'}), 'unicode')  native2unicode(hex2dec({'53' 'c2'}), 'unicode')  native2unicode(hex2dec({'80' '03'}), 'unicode')  native2unicode(hex2dec({'70' 'b9'}), 'unicode')  native2unicode(hex2dec({'ff' '0c'}), 'unicode') 'z ' native2unicode(hex2dec({'57' '50'}), 'unicode')  native2unicode(hex2dec({'68' '07'}), 'unicode') ]});
model.result.numerical('gev1').setResult;
model.result.evaluationGroup('std1EvgFrq').label([native2unicode(hex2dec({'72' '79'}), 'unicode')  native2unicode(hex2dec({'5f' '81'}), 'unicode')  native2unicode(hex2dec({'98' '91'}), 'unicode')  native2unicode(hex2dec({'73' '87'}), 'unicode') ' (' native2unicode(hex2dec({'78' '14'}), 'unicode')  native2unicode(hex2dec({'7a' '76'}), 'unicode') ' 1)']);
model.result.evaluationGroup('std1EvgFrq').set('data', 'dset2');
model.result.evaluationGroup('std1EvgFrq').set('looplevelinput', {'all' 'all'});
model.result.evaluationGroup('std1EvgFrq').feature('gev1').set('expr', {'2*pi*freq' 'imag(freq)/abs(freq)' 'abs(freq)/imag(freq)/2'});
model.result.evaluationGroup('std1EvgFrq').feature('gev1').set('unit', {'rad/s' '1' '1'});
model.result.evaluationGroup('std1EvgFrq').feature('gev1').set('descr', {[native2unicode(hex2dec({'89' 'd2'}), 'unicode')  native2unicode(hex2dec({'98' '91'}), 'unicode')  native2unicode(hex2dec({'73' '87'}), 'unicode') ] [native2unicode(hex2dec({'96' '3b'}), 'unicode')  native2unicode(hex2dec({'5c' '3c'}), 'unicode')  native2unicode(hex2dec({'6b' 'd4'}), 'unicode') ] [native2unicode(hex2dec({'54' 'c1'}), 'unicode')  native2unicode(hex2dec({'8d' '28'}), 'unicode')  native2unicode(hex2dec({'56' 'e0'}), 'unicode')  native2unicode(hex2dec({'5b' '50'}), 'unicode') ]});
model.result.evaluationGroup('std1EvgFrq').feature('gev1').set('const', {'solid.refpntx' '0' [native2unicode(hex2dec({'52' '9b'}), 'unicode')  native2unicode(hex2dec({'77' 'e9'}), 'unicode')  native2unicode(hex2dec({'8b' 'a1'}), 'unicode')  native2unicode(hex2dec({'7b' '97'}), 'unicode')  native2unicode(hex2dec({'53' 'c2'}), 'unicode')  native2unicode(hex2dec({'80' '03'}), 'unicode')  native2unicode(hex2dec({'70' 'b9'}), 'unicode')  native2unicode(hex2dec({'ff' '0c'}), 'unicode') 'x ' native2unicode(hex2dec({'57' '50'}), 'unicode')  native2unicode(hex2dec({'68' '07'}), 'unicode') ]; 'solid.refpnty' '0' [native2unicode(hex2dec({'52' '9b'}), 'unicode')  native2unicode(hex2dec({'77' 'e9'}), 'unicode')  native2unicode(hex2dec({'8b' 'a1'}), 'unicode')  native2unicode(hex2dec({'7b' '97'}), 'unicode')  native2unicode(hex2dec({'53' 'c2'}), 'unicode')  native2unicode(hex2dec({'80' '03'}), 'unicode')  native2unicode(hex2dec({'70' 'b9'}), 'unicode')  native2unicode(hex2dec({'ff' '0c'}), 'unicode') 'y ' native2unicode(hex2dec({'57' '50'}), 'unicode')  native2unicode(hex2dec({'68' '07'}), 'unicode') ]; 'solid.refpntz' '0' [native2unicode(hex2dec({'52' '9b'}), 'unicode')  native2unicode(hex2dec({'77' 'e9'}), 'unicode')  native2unicode(hex2dec({'8b' 'a1'}), 'unicode')  native2unicode(hex2dec({'7b' '97'}), 'unicode')  native2unicode(hex2dec({'53' 'c2'}), 'unicode')  native2unicode(hex2dec({'80' '03'}), 'unicode')  native2unicode(hex2dec({'70' 'b9'}), 'unicode')  native2unicode(hex2dec({'ff' '0c'}), 'unicode') 'z ' native2unicode(hex2dec({'57' '50'}), 'unicode')  native2unicode(hex2dec({'68' '07'}), 'unicode') ]});
model.result.evaluationGroup('std1EvgFrq').run;
model.result.evaluationGroup('std1mpf1').label([native2unicode(hex2dec({'53' 'c2'}), 'unicode')  native2unicode(hex2dec({'4e' '0e'}), 'unicode')  native2unicode(hex2dec({'56' 'e0'}), 'unicode')  native2unicode(hex2dec({'5b' '50'}), 'unicode') ' (' native2unicode(hex2dec({'78' '14'}), 'unicode')  native2unicode(hex2dec({'7a' '76'}), 'unicode') ' 1)']);
model.result.evaluationGroup('std1mpf1').set('data', 'dset2');
model.result.evaluationGroup('std1mpf1').set('looplevelinput', {'all' 'all'});
model.result.evaluationGroup('std1mpf1').feature('gev1').set('expr', {'mpf1.pfLnormX' 'mpf1.pfLnormY' 'mpf1.pfLnormZ' 'mpf1.pfRnormX' 'mpf1.pfRnormY' 'mpf1.pfRnormZ' 'mpf1.mEffLX' 'mpf1.mEffLY' 'mpf1.mEffLZ' 'mpf1.mEffRX'  ...
'mpf1.mEffRY' 'mpf1.mEffRZ'});
model.result.evaluationGroup('std1mpf1').feature('gev1').set('unit', {'1' '1' '1' '1' '1' '1' 'kg' 'kg' 'kg' 'kg*m^2'  ...
'kg*m^2' 'kg*m^2'});
model.result.evaluationGroup('std1mpf1').feature('gev1').set('descr', {[native2unicode(hex2dec({'53' 'c2'}), 'unicode')  native2unicode(hex2dec({'4e' '0e'}), 'unicode')  native2unicode(hex2dec({'56' 'e0'}), 'unicode')  native2unicode(hex2dec({'5b' '50'}), 'unicode')  native2unicode(hex2dec({'ff' '0c'}), 'unicode')  native2unicode(hex2dec({'5f' '52'}), 'unicode')  native2unicode(hex2dec({'4e' '00'}), 'unicode')  native2unicode(hex2dec({'53' '16'}), 'unicode')  native2unicode(hex2dec({'ff' '0c'}), 'unicode') 'X ' native2unicode(hex2dec({'5e' '73'}), 'unicode')  native2unicode(hex2dec({'79' 'fb'}), 'unicode') ] [native2unicode(hex2dec({'53' 'c2'}), 'unicode')  native2unicode(hex2dec({'4e' '0e'}), 'unicode')  native2unicode(hex2dec({'56' 'e0'}), 'unicode')  native2unicode(hex2dec({'5b' '50'}), 'unicode')  native2unicode(hex2dec({'ff' '0c'}), 'unicode')  native2unicode(hex2dec({'5f' '52'}), 'unicode')  native2unicode(hex2dec({'4e' '00'}), 'unicode')  native2unicode(hex2dec({'53' '16'}), 'unicode')  native2unicode(hex2dec({'ff' '0c'}), 'unicode') 'Y ' native2unicode(hex2dec({'5e' '73'}), 'unicode')  native2unicode(hex2dec({'79' 'fb'}), 'unicode') ] [native2unicode(hex2dec({'53' 'c2'}), 'unicode')  native2unicode(hex2dec({'4e' '0e'}), 'unicode')  native2unicode(hex2dec({'56' 'e0'}), 'unicode')  native2unicode(hex2dec({'5b' '50'}), 'unicode')  native2unicode(hex2dec({'ff' '0c'}), 'unicode')  native2unicode(hex2dec({'5f' '52'}), 'unicode')  native2unicode(hex2dec({'4e' '00'}), 'unicode')  native2unicode(hex2dec({'53' '16'}), 'unicode')  native2unicode(hex2dec({'ff' '0c'}), 'unicode') 'Z ' native2unicode(hex2dec({'5e' '73'}), 'unicode')  native2unicode(hex2dec({'79' 'fb'}), 'unicode') ] [native2unicode(hex2dec({'53' 'c2'}), 'unicode')  native2unicode(hex2dec({'4e' '0e'}), 'unicode')  native2unicode(hex2dec({'56' 'e0'}), 'unicode')  native2unicode(hex2dec({'5b' '50'}), 'unicode')  native2unicode(hex2dec({'ff' '0c'}), 'unicode')  native2unicode(hex2dec({'5f' '52'}), 'unicode')  native2unicode(hex2dec({'4e' '00'}), 'unicode')  native2unicode(hex2dec({'53' '16'}), 'unicode')  native2unicode(hex2dec({'ff' '0c'}), 'unicode') 'X ' native2unicode(hex2dec({'65' 'cb'}), 'unicode')  native2unicode(hex2dec({'8f' '6c'}), 'unicode') ] [native2unicode(hex2dec({'53' 'c2'}), 'unicode')  native2unicode(hex2dec({'4e' '0e'}), 'unicode')  native2unicode(hex2dec({'56' 'e0'}), 'unicode')  native2unicode(hex2dec({'5b' '50'}), 'unicode')  native2unicode(hex2dec({'ff' '0c'}), 'unicode')  native2unicode(hex2dec({'5f' '52'}), 'unicode')  native2unicode(hex2dec({'4e' '00'}), 'unicode')  native2unicode(hex2dec({'53' '16'}), 'unicode')  native2unicode(hex2dec({'ff' '0c'}), 'unicode') 'Y ' native2unicode(hex2dec({'65' 'cb'}), 'unicode')  native2unicode(hex2dec({'8f' '6c'}), 'unicode') ] [native2unicode(hex2dec({'53' 'c2'}), 'unicode')  native2unicode(hex2dec({'4e' '0e'}), 'unicode')  native2unicode(hex2dec({'56' 'e0'}), 'unicode')  native2unicode(hex2dec({'5b' '50'}), 'unicode')  native2unicode(hex2dec({'ff' '0c'}), 'unicode')  native2unicode(hex2dec({'5f' '52'}), 'unicode')  native2unicode(hex2dec({'4e' '00'}), 'unicode')  native2unicode(hex2dec({'53' '16'}), 'unicode')  native2unicode(hex2dec({'ff' '0c'}), 'unicode') 'Z ' native2unicode(hex2dec({'65' 'cb'}), 'unicode')  native2unicode(hex2dec({'8f' '6c'}), 'unicode') ] [native2unicode(hex2dec({'67' '09'}), 'unicode')  native2unicode(hex2dec({'65' '48'}), 'unicode')  native2unicode(hex2dec({'6a' '21'}), 'unicode')  native2unicode(hex2dec({'60' '01'}), 'unicode')  native2unicode(hex2dec({'8d' '28'}), 'unicode')  native2unicode(hex2dec({'91' 'cf'}), 'unicode')  native2unicode(hex2dec({'ff' '0c'}), 'unicode') 'X ' native2unicode(hex2dec({'5e' '73'}), 'unicode')  native2unicode(hex2dec({'79' 'fb'}), 'unicode') ] [native2unicode(hex2dec({'67' '09'}), 'unicode')  native2unicode(hex2dec({'65' '48'}), 'unicode')  native2unicode(hex2dec({'6a' '21'}), 'unicode')  native2unicode(hex2dec({'60' '01'}), 'unicode')  native2unicode(hex2dec({'8d' '28'}), 'unicode')  native2unicode(hex2dec({'91' 'cf'}), 'unicode')  native2unicode(hex2dec({'ff' '0c'}), 'unicode') 'Y ' native2unicode(hex2dec({'5e' '73'}), 'unicode')  native2unicode(hex2dec({'79' 'fb'}), 'unicode') ] [native2unicode(hex2dec({'67' '09'}), 'unicode')  native2unicode(hex2dec({'65' '48'}), 'unicode')  native2unicode(hex2dec({'6a' '21'}), 'unicode')  native2unicode(hex2dec({'60' '01'}), 'unicode')  native2unicode(hex2dec({'8d' '28'}), 'unicode')  native2unicode(hex2dec({'91' 'cf'}), 'unicode')  native2unicode(hex2dec({'ff' '0c'}), 'unicode') 'Z ' native2unicode(hex2dec({'5e' '73'}), 'unicode')  native2unicode(hex2dec({'79' 'fb'}), 'unicode') ] [native2unicode(hex2dec({'67' '09'}), 'unicode')  native2unicode(hex2dec({'65' '48'}), 'unicode')  native2unicode(hex2dec({'6a' '21'}), 'unicode')  native2unicode(hex2dec({'60' '01'}), 'unicode')  native2unicode(hex2dec({'8d' '28'}), 'unicode')  native2unicode(hex2dec({'91' 'cf'}), 'unicode')  native2unicode(hex2dec({'ff' '0c'}), 'unicode') 'X ' native2unicode(hex2dec({'65' 'cb'}), 'unicode')  native2unicode(hex2dec({'8f' '6c'}), 'unicode') ]  ...
[native2unicode(hex2dec({'67' '09'}), 'unicode')  native2unicode(hex2dec({'65' '48'}), 'unicode')  native2unicode(hex2dec({'6a' '21'}), 'unicode')  native2unicode(hex2dec({'60' '01'}), 'unicode')  native2unicode(hex2dec({'8d' '28'}), 'unicode')  native2unicode(hex2dec({'91' 'cf'}), 'unicode')  native2unicode(hex2dec({'ff' '0c'}), 'unicode') 'Y ' native2unicode(hex2dec({'65' 'cb'}), 'unicode')  native2unicode(hex2dec({'8f' '6c'}), 'unicode') ] [native2unicode(hex2dec({'67' '09'}), 'unicode')  native2unicode(hex2dec({'65' '48'}), 'unicode')  native2unicode(hex2dec({'6a' '21'}), 'unicode')  native2unicode(hex2dec({'60' '01'}), 'unicode')  native2unicode(hex2dec({'8d' '28'}), 'unicode')  native2unicode(hex2dec({'91' 'cf'}), 'unicode')  native2unicode(hex2dec({'ff' '0c'}), 'unicode') 'Z ' native2unicode(hex2dec({'65' 'cb'}), 'unicode')  native2unicode(hex2dec({'8f' '6c'}), 'unicode') ]});
model.result.evaluationGroup('std1mpf1').feature('gev1').set('const', {'solid.refpntx' '0' [native2unicode(hex2dec({'52' '9b'}), 'unicode')  native2unicode(hex2dec({'77' 'e9'}), 'unicode')  native2unicode(hex2dec({'8b' 'a1'}), 'unicode')  native2unicode(hex2dec({'7b' '97'}), 'unicode')  native2unicode(hex2dec({'53' 'c2'}), 'unicode')  native2unicode(hex2dec({'80' '03'}), 'unicode')  native2unicode(hex2dec({'70' 'b9'}), 'unicode')  native2unicode(hex2dec({'ff' '0c'}), 'unicode') 'x ' native2unicode(hex2dec({'57' '50'}), 'unicode')  native2unicode(hex2dec({'68' '07'}), 'unicode') ]; 'solid.refpnty' '0' [native2unicode(hex2dec({'52' '9b'}), 'unicode')  native2unicode(hex2dec({'77' 'e9'}), 'unicode')  native2unicode(hex2dec({'8b' 'a1'}), 'unicode')  native2unicode(hex2dec({'7b' '97'}), 'unicode')  native2unicode(hex2dec({'53' 'c2'}), 'unicode')  native2unicode(hex2dec({'80' '03'}), 'unicode')  native2unicode(hex2dec({'70' 'b9'}), 'unicode')  native2unicode(hex2dec({'ff' '0c'}), 'unicode') 'y ' native2unicode(hex2dec({'57' '50'}), 'unicode')  native2unicode(hex2dec({'68' '07'}), 'unicode') ]; 'solid.refpntz' '0' [native2unicode(hex2dec({'52' '9b'}), 'unicode')  native2unicode(hex2dec({'77' 'e9'}), 'unicode')  native2unicode(hex2dec({'8b' 'a1'}), 'unicode')  native2unicode(hex2dec({'7b' '97'}), 'unicode')  native2unicode(hex2dec({'53' 'c2'}), 'unicode')  native2unicode(hex2dec({'80' '03'}), 'unicode')  native2unicode(hex2dec({'70' 'b9'}), 'unicode')  native2unicode(hex2dec({'ff' '0c'}), 'unicode') 'z ' native2unicode(hex2dec({'57' '50'}), 'unicode')  native2unicode(hex2dec({'68' '07'}), 'unicode') ]});
model.result.evaluationGroup('std1mpf1').run;
model.result('pg1').label([native2unicode(hex2dec({'63' '2f'}), 'unicode')  native2unicode(hex2dec({'57' '8b'}), 'unicode') ' (solid)']);
model.result('pg1').set('looplevel', [1 14]);
model.result('pg1').set('frametype', 'spatial');
model.result('pg1').set('showlegends', false);
model.result('pg1').feature('surf1').set('const', {'solid.refpntx' '0' [native2unicode(hex2dec({'52' '9b'}), 'unicode')  native2unicode(hex2dec({'77' 'e9'}), 'unicode')  native2unicode(hex2dec({'8b' 'a1'}), 'unicode')  native2unicode(hex2dec({'7b' '97'}), 'unicode')  native2unicode(hex2dec({'53' 'c2'}), 'unicode')  native2unicode(hex2dec({'80' '03'}), 'unicode')  native2unicode(hex2dec({'70' 'b9'}), 'unicode')  native2unicode(hex2dec({'ff' '0c'}), 'unicode') 'x ' native2unicode(hex2dec({'57' '50'}), 'unicode')  native2unicode(hex2dec({'68' '07'}), 'unicode') ]; 'solid.refpnty' '0' [native2unicode(hex2dec({'52' '9b'}), 'unicode')  native2unicode(hex2dec({'77' 'e9'}), 'unicode')  native2unicode(hex2dec({'8b' 'a1'}), 'unicode')  native2unicode(hex2dec({'7b' '97'}), 'unicode')  native2unicode(hex2dec({'53' 'c2'}), 'unicode')  native2unicode(hex2dec({'80' '03'}), 'unicode')  native2unicode(hex2dec({'70' 'b9'}), 'unicode')  native2unicode(hex2dec({'ff' '0c'}), 'unicode') 'y ' native2unicode(hex2dec({'57' '50'}), 'unicode')  native2unicode(hex2dec({'68' '07'}), 'unicode') ]; 'solid.refpntz' '0' [native2unicode(hex2dec({'52' '9b'}), 'unicode')  native2unicode(hex2dec({'77' 'e9'}), 'unicode')  native2unicode(hex2dec({'8b' 'a1'}), 'unicode')  native2unicode(hex2dec({'7b' '97'}), 'unicode')  native2unicode(hex2dec({'53' 'c2'}), 'unicode')  native2unicode(hex2dec({'80' '03'}), 'unicode')  native2unicode(hex2dec({'70' 'b9'}), 'unicode')  native2unicode(hex2dec({'ff' '0c'}), 'unicode') 'z ' native2unicode(hex2dec({'57' '50'}), 'unicode')  native2unicode(hex2dec({'68' '07'}), 'unicode') ]});
model.result('pg1').feature('surf1').set('colortable', 'AuroraBorealis');
model.result('pg1').feature('surf1').set('threshold', 'manual');
model.result('pg1').feature('surf1').set('thresholdvalue', 0.2);
model.result('pg1').feature('surf1').set('resolution', 'normal');
model.result('pg1').feature('surf1').feature('def').set('scale', 50115.73474882905);
model.result('pg1').feature('surf1').feature('def').set('scaleactive', false);
model.result('pg2').set('xlabel', 'k');
model.result('pg2').set('ylabel', [native2unicode(hex2dec({'98' '91'}), 'unicode')  native2unicode(hex2dec({'73' '87'}), 'unicode') ' (Hz)']);
model.result('pg2').set('showlegends', false);
model.result('pg2').set('xlabelactive', false);
model.result('pg2').set('ylabelactive', false);
model.result('pg2').feature('glob1').set('unit', {'Hz'});
model.result('pg2').feature('glob1').set('descr', {[native2unicode(hex2dec({'98' '91'}), 'unicode')  native2unicode(hex2dec({'73' '87'}), 'unicode') ]});
model.result('pg2').feature('glob1').set('const', {'solid.refpntx' '0' [native2unicode(hex2dec({'52' '9b'}), 'unicode')  native2unicode(hex2dec({'77' 'e9'}), 'unicode')  native2unicode(hex2dec({'8b' 'a1'}), 'unicode')  native2unicode(hex2dec({'7b' '97'}), 'unicode')  native2unicode(hex2dec({'53' 'c2'}), 'unicode')  native2unicode(hex2dec({'80' '03'}), 'unicode')  native2unicode(hex2dec({'70' 'b9'}), 'unicode')  native2unicode(hex2dec({'ff' '0c'}), 'unicode') 'x ' native2unicode(hex2dec({'57' '50'}), 'unicode')  native2unicode(hex2dec({'68' '07'}), 'unicode') ]; 'solid.refpnty' '0' [native2unicode(hex2dec({'52' '9b'}), 'unicode')  native2unicode(hex2dec({'77' 'e9'}), 'unicode')  native2unicode(hex2dec({'8b' 'a1'}), 'unicode')  native2unicode(hex2dec({'7b' '97'}), 'unicode')  native2unicode(hex2dec({'53' 'c2'}), 'unicode')  native2unicode(hex2dec({'80' '03'}), 'unicode')  native2unicode(hex2dec({'70' 'b9'}), 'unicode')  native2unicode(hex2dec({'ff' '0c'}), 'unicode') 'y ' native2unicode(hex2dec({'57' '50'}), 'unicode')  native2unicode(hex2dec({'68' '07'}), 'unicode') ]; 'solid.refpntz' '0' [native2unicode(hex2dec({'52' '9b'}), 'unicode')  native2unicode(hex2dec({'77' 'e9'}), 'unicode')  native2unicode(hex2dec({'8b' 'a1'}), 'unicode')  native2unicode(hex2dec({'7b' '97'}), 'unicode')  native2unicode(hex2dec({'53' 'c2'}), 'unicode')  native2unicode(hex2dec({'80' '03'}), 'unicode')  native2unicode(hex2dec({'70' 'b9'}), 'unicode')  native2unicode(hex2dec({'ff' '0c'}), 'unicode') 'z ' native2unicode(hex2dec({'57' '50'}), 'unicode')  native2unicode(hex2dec({'68' '07'}), 'unicode') ]});
model.result('pg2').feature('glob1').set('xdatasolnumtype', 'outer');
model.result('pg2').feature('glob1').set('linecolor', 'black');
model.result('pg2').feature('glob1').set('linewidth', 'preference');

out = model;
