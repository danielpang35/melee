#include "CombatTuningPanel.h"
#include "Training/CombatLabGameMode.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/Layout/SScrollBox.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/Text/STextBlock.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/Input/SSpinBox.h"
#include "Styling/CoreStyle.h"

void SCombatTuningPanel::Construct(const FArguments& Args)
{
    Lab=Args._Lab;
    TSharedRef<SVerticalBox> Rows=SNew(SVerticalBox);
    FString LastGroup;
    for(const auto E:Lab->Combat.tuning.entries()){
        FString Group=UTF8_TO_TCHAR(E.group);
        if(Group!=LastGroup){Rows->AddSlot().AutoHeight().Padding(0,14,0,5)[SNew(STextBlock).Text(FText::FromString(Group.ToUpper())).ColorAndOpacity(FLinearColor(.4f,.8f,1))];LastGroup=Group;}
        Rows->AddSlot().AutoHeight().Padding(0,2)[SNew(SHorizontalBox)
            +SHorizontalBox::Slot().FillWidth(1).VAlign(VAlign_Center)[SNew(STextBlock).Text(FText::FromString(UTF8_TO_TCHAR(E.name)))]
            +SHorizontalBox::Slot().AutoWidth()[SNew(SBox).WidthOverride(150)[SNew(SSpinBox<double>)
                .MinValue(E.minimum).MaxValue(E.maximum).Delta((E.maximum-E.minimum)/200.)
                .Value_Lambda([Weak=Lab,Name=FString(UTF8_TO_TCHAR(E.name))](){if(Weak.IsValid())for(auto Entry:Weak->Combat.tuning.entries())if(Name==UTF8_TO_TCHAR(Entry.name))return *Entry.value;return 0.;})
                .OnValueChanged_Lambda([Weak=Lab,Name=FString(UTF8_TO_TCHAR(E.name))](double Value){if(Weak.IsValid())for(auto Entry:Weak->Combat.tuning.entries())if(Name==UTF8_TO_TCHAR(Entry.name))*Entry.value=FMath::Clamp(Value,Entry.minimum,Entry.maximum);})]]];
    }
    auto Button=[this](const TCHAR* Text,TFunction<void(ACombatLabGameMode*)> Action){return SNew(SButton).Text(FText::FromString(Text)).OnClicked_Lambda([Weak=Lab,Action](){if(Weak.IsValid())Action(Weak.Get());return FReply::Handled();});};
    ChildSlot.HAlign(HAlign_Right).VAlign(VAlign_Center).Padding(24)[SNew(SBox).WidthOverride(520).HeightOverride(760)
        [SNew(SBorder).BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush")).BorderBackgroundColor(FLinearColor(.015f,.025f,.04f,1.f)).Padding(20)[SNew(SVerticalBox)
            +SVerticalBox::Slot().AutoHeight()[SNew(STextBlock).Text(FText::FromString(TEXT("COMBAT TUNING"))).ColorAndOpacity(FLinearColor(.5f,.85f,1))]
            +SVerticalBox::Slot().AutoHeight().Padding(0,8)[SNew(STextBlock).Text(FText::FromString(TEXT("Simulation paused while tuning. Durations: seconds.\nDistances: cm. Turn rates: degrees/sec.")))]
            +SVerticalBox::Slot().FillHeight(1)[SNew(SScrollBox)+SScrollBox::Slot()[Rows]]
            +SVerticalBox::Slot().AutoHeight().Padding(0,10)[SNew(SHorizontalBox)
                +SHorizontalBox::Slot()[Button(TEXT("RESET"),[](auto* L){L->ResetTuning();})]
                +SHorizontalBox::Slot()[Button(TEXT("SAVE"),[](auto* L){L->SaveTuning();})]
                +SHorizontalBox::Slot()[Button(TEXT("LOAD"),[](auto* L){L->LoadTuning();})]
                +SHorizontalBox::Slot()[Button(TEXT("CLOSE"),[](auto* L){L->ToggleTuning();})]]
            +SVerticalBox::Slot().AutoHeight()[Button(TEXT("PROMOTE TO PROJECT DEFAULTS"),[](auto* L){L->SaveTuning(true);})]
            +SVerticalBox::Slot().AutoHeight().Padding(0,8)[SNew(STextBlock).AutoWrapText(true).Text_Lambda([Weak=Lab](){return FText::FromString(Weak.IsValid()?Weak->TuningStatus:FString());})]
        ]]];
}
