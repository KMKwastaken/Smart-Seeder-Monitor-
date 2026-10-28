// Educational simulation only. No hardware interfaces or control outputs.
#include <iostream>
#include <iomanip>
#include <string>
#include <stdexcept>
#include <cmath>
#include <vector>

struct Reading { double speed, flow, tank, rpm; bool connected; };
class Detector {
 int blockedTicks=0;
public:
 std::vector<std::string> evaluate(const Reading& r) {
  std::vector<std::string> faults;
  if (!r.connected) { blockedTicks=0; return {"SENSOR_LOSS"}; }
  if (!std::isfinite(r.flow) || r.flow<0 || r.tank<0 || r.tank>100 || r.rpm<0 || r.speed<0) {
   blockedTicks=0; return {"INVALID_SENSOR"};
  }
  blockedTicks = r.speed>1.0 && r.flow<5.0 ? blockedTicks+1 : 0;
  if(blockedTicks>=3) faults.push_back("BLOCKAGE");
  if(r.tank<15.0) faults.push_back("LOW_TANK");
  if(r.speed>1.0 && r.rpm<2000.0) faults.push_back("LOW_FAN");
  return faults;
 }
};
int number(const std::string& s) {
 size_t n=0; int v=std::stoi(s,&n); if(n!=s.size()) throw std::invalid_argument("integer required");return v;
}
int main(int argc,char** argv) {
 try {
  int ticks=60; std::string scenario="demo"; bool probe=false; Reading input{};
  for(int i=1;i<argc;++i) {
   std::string a=argv[i];
   if(a=="--help") { std::cout<<"SIMULATION ONLY\n--ticks 1..100000 --scenario normal|blockage|low-tank|low-fan|sensor-loss|stopped|demo\n--probe speed flow tank rpm connected(0|1) [--ticks N]\n";return 0; }
   if(a=="--ticks" && i+1<argc) ticks=number(argv[++i]);
   else if(a=="--scenario" && i+1<argc) scenario=argv[++i];
   else if(a=="--probe" && i+5<argc) {
    probe=true; input.speed=std::stod(argv[++i]);input.flow=std::stod(argv[++i]);
    input.tank=std::stod(argv[++i]);input.rpm=std::stod(argv[++i]);int c=number(argv[++i]);
    if(c!=0&&c!=1) throw std::invalid_argument("connected must be 0 or 1");input.connected=c==1;
   } else throw std::invalid_argument("unknown or incomplete argument: "+a);
  }
  if(ticks<1||ticks>100000) throw std::invalid_argument("ticks outside 1..100000");
  const std::vector<std::string> names={"normal","blockage","low-tank","low-fan","sensor-loss","stopped","demo"};
  bool known=false;for(auto& n:names) if(n==scenario) known=true;
  if(!known) throw std::invalid_argument("unknown scenario");
  Detector detector;std::cout<<std::fixed<<std::setprecision(2);
  for(int t=0;t<ticks;++t) {
   Reading r{8.0,40.0+2*std::sin(t*0.4),80.0-t*0.01,3200.0,true};
   std::string mode=scenario;
   if(mode=="demo") mode=t>=10&&t<20?"blockage":t>=25&&t<35?"low-tank":t>=40&&t<45?"low-fan":t>=50&&t<55?"sensor-loss":"normal";
   if(mode=="blockage") r.flow=0;
   if(mode=="low-tank") r.tank=10;
   if(mode=="low-fan") r.rpm=1400;
   if(mode=="sensor-loss") r.connected=false;
   if(mode=="stopped") {r.speed=0;r.flow=0;r.rpm=0;}
   if(probe) r=input;
   // JSON cannot represent non-finite numbers; reject before serialization.
   if(!std::isfinite(r.speed)||!std::isfinite(r.flow)||!std::isfinite(r.tank)||!std::isfinite(r.rpm)) throw std::invalid_argument("finite readings required");
   auto faults=detector.evaluate(r);
   std::cout<<"{\"schema\":1,\"simulated\":true,\"tick\":"<<t<<",\"time_s\":"<<t
    <<",\"speed_kph\":"<<r.speed<<",\"flow_seeds_s\":"<<r.flow<<",\"tank_pct\":"<<r.tank
    <<",\"fan_rpm\":"<<r.rpm<<",\"connected\":"<<(r.connected?"true":"false")<<",\"faults\":[";
   for(size_t i=0;i<faults.size();++i) std::cout<<(i?",":"")<<"\""<<faults[i]<<"\"";
   std::cout<<"]}\n";
  }
 } catch(const std::exception& e) {std::cerr<<"Error: "<<e.what()<<"\n";return 2;}
}
