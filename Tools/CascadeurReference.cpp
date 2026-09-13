#include "Combat/CombatSimulation.h"
#include <fstream>
#include <iomanip>
#include <iostream>
#include <string>
using namespace mcl;
int main(int argc,char** argv)
{
    if(argc!=4&&argc!=5){std::cerr<<"Usage: reference tuning.tsv output.csv angle [weapon.csv]\n";return 2;}
    Tuning tuning;std::ifstream settings(argv[1]);std::string name;double value;
    if(!settings)return 3;
    while(settings>>name>>value)for(auto entry:tuning.entries())if(name==entry.name)*entry.value=value;
    const double angle=std::stod(argv[3]);
    Combatant actor;actor.reset({0,0,88},{},tuning);
    if(argc==5){
        std::ifstream file(argv[4]);auto clip=std::make_shared<AuthoredRightCut>();
        if(!clip->read(file)){std::cerr<<"Invalid authored weapon track\n";return 6;}
        actor.rightCut=clip;
    }
    std::ofstream out(argv[2]);if(!out)return 4;
    out<<std::setprecision(12)<<"frame,seconds,phase,progress,hilt_x,hilt_y,hilt_z,tip_x,tip_y,tip_z,edge_x,edge_y,edge_z,right_x,right_y,right_z,left_x,left_y,left_z\n";
    const auto vec=[&](Vec p){out<<','<<p.x<<','<<p.y<<','<<p.z;};
    // 120fps source, sampled from the actual 240Hz combat evaluator. The .575,
    // .500 and .675 second boundaries all land on exact source frames.
    for(int tick=0;tick<=540;++tick){
        if(tick==60&&!actor.start({AttackKind::Strike,angle,angle},tuning))return 5;
        if(tick%2==0){
            const Vec axis=(actor.weapon.tip-actor.weapon.hilt).normal();
            out<<tick/2+1<<','<<tick/240.<<','<<phaseName(actor.state.phase)<<','<<actor.state.progress();
            vec(actor.weapon.hilt);vec(actor.weapon.tip);vec(actor.weapon.edge);
            vec(actor.weapon.hilt-axis*(tuning.BladeLength*.12/1.103061375617981));
            vec(actor.weapon.hilt-axis*(tuning.BladeLength*.23/1.103061375617981));out<<'\n';
        }
        actor.advance(1./240.,tuning);
    }
    std::cout<<"Exported 271 source frames at 120fps; gameplay evaluator unchanged\n";
}
