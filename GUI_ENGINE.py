import pygame
import time

def CheckType(Variable, Type):
    try:
        Type(Variable)
        return True
    except (TypeError, ValueError):
        return False

# Base Gui Class
class GUI:
    def __init__(self, display_width, display_height, Title, BC):
        pygame.init()
        pygame.font.init()
        self.PreviousLoadTime = time.time()
        self.Colours = {"White": (255, 255, 255), "Black": (0, 0, 0), "Blue": (0, 0, 255), "Red": (255, 0, 0),
                        "Gray": (124, 124, 124)}
        if BC in self.Colours:
            self.BC = self.Colours[BC]
        else:
            self.BC = BC
        self.Scrolls, self.Lines, self.Rectangles = list(), list(), list()
        self.EntryFields, self.Texts, self.Buttons = list(), list(), list()
        self.Images = list()
        self.Display = pygame.display.set_mode((display_width, display_height))
        pygame.display.set_caption(Title)
        self.Display.fill(self.BC)
        self.TempItem, self.KeysDown = None, list()
        self.MDown, self.KDown = False, False

    def Load(self, Refresh=False):
        Events = pygame.event.get()
        for event in Events:
            if event.type == pygame.MOUSEBUTTONDOWN or self.MDown:
                if pygame.mouse.get_pressed()[0] == 1:
                    self.MDown = True
                else:
                    self.MDown = False
            if event.type == pygame.MOUSEBUTTONUP:
                if pygame.mouse.get_pressed()[0] == 0:
                    self.MDown = False
            if event.type == pygame.KEYDOWN:
                if hasattr(event, "key"):
                    self.KeysDown.append(event)
                    self.KDown = True
            elif event.type == pygame.KEYUP:
                for KeyEvent in self.KeysDown:
                    if KeyEvent.key == event.key:
                        self.KeysDown.remove(KeyEvent)
                if len(self.KeysDown) == 0:
                    self.KDown = False
            if event.type == pygame.QUIT:
                pygame.quit()
        if self.MDown:
            x, y = pygame.mouse.get_pos()
            for scroll in self.Scrolls:
                scroll.In_Box(x, y)
            for entryField in self.EntryFields:
                entryField.In_Box(x, y)
            for button in self.Buttons:
                button.In_Box(x, y)

        if self.KDown and time.time() - self.PreviousLoadTime > 0.03:
            self.PreviousLoadTime = time.time()
            for entryField in self.EntryFields:
                if not entryField.Listening:
                    continue
                for Event in self.KeysDown:
                    if time.time() - entryField.PreviousTime <= entryField.InputWait and Event.key == entryField.PreviousKey:
                        continue
                    entryField.PreviousTime = time.time()
                    if Event.key == pygame.K_RETURN:
                        entryField.LoadEntry()
                    # Getting ride of "else:" and changing the if after to elif
                    elif Event.key != pygame.K_BACKSPACE:
                        try:
                            entryField.Input += Event.unicode
                        except AttributeError:
                            pass
                    elif len(entryField.Input) != 0:
                        entryField.Input = entryField.Input[0:len(entryField.Input) - 1]
                    entryField.AddText()
                    entryField.PreviousKey = Event.key
        if Refresh:
            self.Refresh()

    def Refresh(self):
        self.Display.fill(self.BC)
        ToDraw = list()
        ToDraw.extend(self.Scrolls)
        ToDraw.extend(self.EntryFields)
        ToDraw.extend(self.Buttons)
        ToDraw.extend(self.Rectangles)
        ToDraw.extend(self.Lines)
        ToDraw.extend(self.Texts)
        ToDraw.extend(self.Images)
        ToDraw.append(self.TempItem)
        ToDraw = [item for item in ToDraw if item is not None]
        if not ToDraw:
            return
        ToDraw.sort(key=lambda x: x.Z)
        for Entity in ToDraw:
            Entity.Draw()
        pygame.display.update()

    def Resize(self, display_width, display_height):
        self.Display = pygame.display.set_mode((display_width, display_height))

    def SetBackgroundColour(self, Colour):
        self.Colours = {"White": (255, 255, 255), "Black": (0, 0, 0), "Blue": (0, 0, 255), "Red": (255, 0, 0),
                        "Gray": (124, 124, 124)}
        if Colour in self.Colours:
            self.BC = self.Colours[Colour]
        else:
            self.BC = Colour

    @staticmethod
    def MousePos():
        return pygame.mouse.get_pos()

    @staticmethod
    def Kill():
        pygame.quit()
        quit()

    @staticmethod
    def ChangeTitle(Title):
        pygame.display.set_caption(Title)

# Button Class
class Button:
    def __init__(self, Display, Pos, Size, Thickness, Colour, Command, Arguments=False, Fill=False, FillColour=None, Time=0.1, Z=0):
        self.Z, self.Time, self.Texts, self.Arguments = Z, Time, list(), False if not Arguments else Arguments
        self.State, self.Running = False, False
        self.PreviousTime = time.time()
        self.FillColour, self.Fill = FillColour, Fill
        self.Lines, self.Text = list(), list()
        self.Colours = {"White": (255, 255, 255), "Black": (0, 0, 0), "Blue": (0, 0, 255), "Red": (255, 0, 0),
                        "Gray": (124, 124, 124), "Green": (0, 255, 0)}
        self.DrawPos = (Pos[0], Pos[1], Size[0], Size[1])
        self.Thickness, self.Command = Thickness, Command

        if Colour in self.Colours: self.Colour = self.Colours[Colour]
        else: self.Colour = Colour

        if FillColour in self.Colours: self.FillColour = self.Colours[FillColour]
        else: self.FillColour = FillColour

        self.Positions, self.Display = [Pos[0], Size[0] + Pos[0], Pos[1], Size[1] + Pos[1]], Display

    def Draw(self):
        if not self.Fill: pygame.draw.rect(self.Display, self.Colour, self.DrawPos, self.Thickness)
        else:
            if not self.FillColour:
                pygame.draw.rect(self.Display, self.Colour, self.DrawPos, self.Thickness)
                for i in range(self.Positions[3] - self.Positions[2]):
                    pygame.draw.line(self.Display, self.Colour, (self.Positions[0], self.Positions[2] + i),
                                     (self.Positions[1], self.Positions[2] + i), 1)
            else:
                for i in range(self.Positions[3] - self.Positions[2]):
                    pygame.draw.line(self.Display, self.FillColour, (self.Positions[0], self.Positions[2] + i),
                                     (self.Positions[1] - 1, self.Positions[2] + i), 1)
                pygame.draw.rect(self.Display, self.Colour, self.DrawPos, self.Thickness)
        for line in self.Lines:
            line.Draw()
        for text in self.Texts:
            text.Draw()

    def In_Box(self, x, y):
        if time.time() - self.PreviousTime >= self.Time:
            if self.Positions[0] < x < self.Positions[1] and self.Positions[2] < y < self.Positions[3]:
                self.PreviousTime = time.time()
                if self.Arguments:
                    self.Command(*self.Arguments)
                elif self.Command is not None:
                    self.Command()
                self.State = True
                self.PreviousTime = time.time()
            else:
                self.State = False

    def AttachLine(self, line):
        NewDrawPos = (
            line.DrawPos[0] + self.Positions[0], line.DrawPos[1] + self.Positions[2], line.DrawPos[0] + self.Positions[0],
            line.DrawPos[1] + self.Positions[2])
        line.DrawPos = NewDrawPos
        self.Lines.append(line)

    def AttachText(self, NewText):
        NewText.Pos = (NewText.Pos[0] + self.Positions[0], NewText.Pos[1] + self.Positions[2])
        self.Texts.append(NewText)

# EntryField Class
class EntryField:
    def __init__(self, Display, Pos, Size, Thickness, Colour, Fill=False, FillColour=None, Z=0, Cap=False, InputWait=0.1, InputTypeAllowed=None):
        self.InputWait, self.PreviousTime = InputWait, time.time()
        self.PreviousKey, self.Entry, self.InputTypeAllowed = None, None, InputTypeAllowed
        self.Cap, self.Z = Cap, Z
        self.Fill, self.FillColour = Fill, FillColour
        self.Listening, self.Text = False, False
        self.Input,  self.Thickness= "", Thickness
        self.Colours = {"White": (255, 255, 255), "Black": (0, 0, 0), "Blue": (0, 0, 255), "Red": (255, 0, 0),
                        "Gray": (124, 124, 124), "Green": (0, 255, 0)}
        self.DrawPos = (Pos[0], Pos[1], Size[0], Size[1])

        if Colour in self.Colours: self.Colour = self.Colours[Colour]
        else: self.Colour = Colour

        if FillColour in self.Colours: self.FillColour = self.Colours[FillColour]
        else: self.FillColour = FillColour

        if self.InputTypeAllowed is not None:
            self.Entry = self.InputTypeAllowed()

        self.Positions, self.Display = [Pos[0], Size[0] + Pos[0], Pos[1], Size[1] + Pos[1]], Display

    def LoadEntry(self):
        if self.InputTypeAllowed is not None:
            if not CheckType(self.Input, self.InputTypeAllowed):
                self.Input = ""
            else:
                self.Entry, self.Input = self.InputTypeAllowed(self.Input), ""
                self.AddText()
        else:
            self.Entry, self.Input = self.Input, ""
            self.AddText()

    def Draw(self):
        if not self.Fill:
            pygame.draw.rect(self.Display, self.Colour, self.DrawPos, self.Thickness)
        else:
            if not self.FillColour:
                pygame.draw.rect(self.Display, self.Colour, self.DrawPos, self.Thickness)
                for i in range(self.Positions[3] - self.Positions[2]):
                    pygame.draw.line(self.Display, self.Colour, (self.Positions[0], self.Positions[2] + i),
                                     (self.Positions[1], self.Positions[2] + i), 1)
            else:
                for i in range(self.Positions[3] - self.Positions[2]):
                    pygame.draw.line(self.Display, self.FillColour, (self.Positions[0], self.Positions[2] + i),
                                     (self.Positions[1] - 1, self.Positions[2] + i), 1)
                pygame.draw.rect(self.Display, self.Colour, self.DrawPos, self.Thickness)
        if self.Text:
            self.Text.Draw()

    def In_Box(self, x, y):
        if self.Positions[0] < x < self.Positions[1] and self.Positions[2] < y < self.Positions[3]: self.Listening = True
        else: self.Listening = False

    def AttachText(self, NewText):
        self.Text = NewText
        self.Text.Pos = (self.Text.Pos[0] + self.Positions[0], self.Text.Pos[1] + self.Positions[2])

    def AddText(self):
        if self.Cap:
            if len(self.Input) > self.Cap:
                self.Input = self.Input[:self.Cap]
                return
        self.Text.ChangeText(self.Text.Text + self.Input)

# Text Class
class Text:
    def __init__(self, Display, Font, Size, Position, Colour, Text, Z=0):
        self.Z = Z
        self.Colours = {"White": (255, 255, 255), "Black": (0, 0, 0), "Blue": (0, 0, 255), "Red": (255, 0, 0),
                        "Gray": (124, 124, 124), "Green": (0, 255, 0)}
        self.Pos = Position

        if Colour in self.Colours: self.Colour = self.Colours[Colour]
        else: self.Colour = Colour

        self.Display, self.MyFont = Display, pygame.font.SysFont(Font, Size)
        self.Text, self.RenderedText = Text, self.MyFont.render(Text, False, self.Colour)

    def Draw(self):
        self.Display.blit(self.RenderedText, self.Pos)

    def ChangeText(self, NewText):
        self.RenderedText = self.MyFont.render(NewText, False, self.Colour)

    def NewText(self, NewText):
        self.Text = NewText
        self.ChangeText(NewText)

# Line Class
class Line:
    def __init__(self, Display, Position, Position2, Thickness, Colour, Z=0):
        self.Z, self.Display = Z, Display
        self.DrawPos, self.Thickness = (Position[0], Position[1], Position2[0], Position2[1]), Thickness
        self.Colours = {"White": (255, 255, 255), "Black": (0, 0, 0), "Blue": (0, 0, 255), "Red": (255, 0, 0),
                        "Gray": (124, 124, 124), "Green": (0, 255, 0)}

        if Colour in self.Colours: self.Colour = self.Colours[Colour]
        else: self.Colour = Colour

    def Draw(self):
        pygame.draw.line(self.Display, self.Colour, (self.DrawPos[0], self.DrawPos[1]),
                         (self.DrawPos[2], self.DrawPos[3]), self.Thickness)

# Rectangle Class
class Rectangle:
    def __init__(self, Display, Pos, Size, Thickness, Colour, Fill=False, FillColour=None, Z=0):
        self.Z = Z
        self.Fill, self.FillColour = Fill, FillColour
        self.Lines, self.Rectangles, self.Texts = list(), list(), list()
        self.Colours = {"White": (255, 255, 255), "Black": (0, 0, 0), "Blue": (0, 0, 255), "Red": (255, 0, 0),
                        "Gray": (124, 124, 124), "Green": (0, 255, 0)}
        self.DrawPos, self.Thickness = (Pos[0], Pos[1], Size[0], Size[1]), Thickness

        if Colour in self.Colours: self.Colour = self.Colours[Colour]
        else: self.Colour = Colour

        if FillColour in self.Colours: self.FillColour = self.Colours[FillColour]
        else: self.FillColour = FillColour

        self.Display, self.Positions = Display, [Pos[0], Size[0] + Pos[0], Pos[1], Size[1] + Pos[1]]

    def Draw(self):
        if not self.Fill:
            pygame.draw.rect(self.Display, self.Colour, self.DrawPos, self.Thickness)
        else:
            if not self.FillColour:
                pygame.draw.rect(self.Display, self.Colour, self.DrawPos, self.Thickness)
                for i in range(self.Positions[3] - self.Positions[2]):
                    pygame.draw.line(self.Display, self.Colour, (self.Positions[0], self.Positions[2] + i),
                                     (self.Positions[1], self.Positions[2] + i), 1)
            else:
                for i in range(self.Positions[3] - self.Positions[2]):
                    pygame.draw.line(self.Display, self.FillColour, (self.Positions[0], self.Positions[2] + i),
                                     (self.Positions[1] - 1, self.Positions[2] + i), 1)
                pygame.draw.rect(self.Display, self.Colour, self.DrawPos, self.Thickness)
        for rectangle in self.Rectangles:
            rectangle.Draw()
        for text in self.Texts:
            text.Draw()
        for line in self.Lines:
            line.Draw()

    def AttachLine(self, line):
        NewDrawPos = (line.DrawPos[0] + self.Positions[0], line.DrawPos[1] + self.Positions[2], line.DrawPos[0] + self.Positions[0], line.DrawPos[1] + self.Positions[2])
        line.DrawPos = NewDrawPos
        self.Lines.append(line)

    def AttachText(self, NewText):
        NewText.Pos = (NewText.Pos[0] + self.Positions[0], NewText.Pos[1] + self.Positions[2])
        self.Texts.append(NewText)

# Scroll Class
class Scroll:
    def __init__(self, rectangle, SlideParameters, MaxValue, LowValue, Z=0):
        self.Z = Z
        self.rectangle = rectangle
        self.SlideParameters = SlideParameters
        self.Values = (MaxValue, LowValue)
        self.Positions = rectangle.Positions
        self.DrawPos = self.rectangle.DrawPos
        self.Value = 0
        self.TopValue = self.SlideParameters[1] - self.DrawPos[3] / 2
        self.BottomValue = self.SlideParameters[0] + self.DrawPos[3] / 2
        self.Top = self.SlideParameters[0] + ((self.Positions[2] + self.Positions[3]) / 2)
        self.Bottom = self.SlideParameters[1] - (self.Positions[2] + self.Positions[3]) / 2

    def In_Box(self, x, y):
        if self.Positions[0] < x < self.Positions[1] and self.Positions[2] < y < self.Positions[3]:
            Change = int(y - (self.Positions[2] + self.Positions[3]) / 2)
            if Change + self.Positions[2] >= self.SlideParameters[0] and Change + self.Positions[3] <= \
                    self.SlideParameters[1]:
                self.Positions[2] += Change
                self.Positions[3] += Change
                self.rectangle.DrawPos = (self.Positions[0], self.Positions[2], self.DrawPos[2],
                                          self.DrawPos[3] + y - (self.Positions[2] + self.Positions[3]) / 2)
                self.rectangle.Positions = self.Positions
            elif Change < 0 and self.SlideParameters[1] - self.Positions[3] != 0 and self.SlideParameters[0] - self.Positions[2] != 0:
                self.Positions[2] += self.SlideParameters[0] - self.Positions[2]
                self.rectangle.DrawPos = (self.Positions[0], self.Positions[2], self.DrawPos[2],
                                          self.DrawPos[3] + y - (self.Positions[2] + self.Positions[3]) / 2)
                self.rectangle.Positions = self.Positions
            elif Change > 0 and self.SlideParameters[1] - self.Positions[3] != 0 and self.SlideParameters[0] - self.Positions[2] != 0:
                self.Positions[3] += self.SlideParameters[1] - self.Positions[3]
                self.rectangle.DrawPos = (self.Positions[0], self.Positions[2], self.DrawPos[2],
                                          self.DrawPos[3] + y - (self.Positions[2] + self.Positions[3]) / 2)
                self.rectangle.Positions = self.Positions
        print(self.CalculateValue())

    def CalculateValue(self):
        return (((((self.Positions[2] + self.Positions[3]) / 2) - self.BottomValue) / (
                    self.TopValue - self.BottomValue)) * (self.Values[0] - self.Values[1])) + self.Values[1]

    def Draw(self):
        self.rectangle.Draw()

# Image Class
class Image:
    def __init__(self, Display, Position, File, Z=0):
        self.Img, self.Position = pygame.image.load(File), Position
        self.Display, self.Z = Display, Z

    def Draw(self):
        self.Display.blit(self.Img, self.Position)

# Scene Class
class Scene:
    def __init__(self, Gui):
        self.Gui = Gui
        self.Scrolls, self.Lines, self.Rectangles = list(), list(), list()
        self.EntryFields, self.Texts, self.Buttons = list(), list(), list()
        self.Images = list()

    def JoinGui(self):
        for Entity in self.Scrolls:
            if Entity not in self.Gui.Scrolls:
                self.Gui.Scrolls.append(Entity)
        for Entity in self.Lines:
            if Entity not in self.Gui.Lines:
                self.Gui.Lines.append(Entity)
        for Entity in self.Rectangles:
            if Entity not in self.Gui.Rectangles:
                self.Gui.Rectangles.append(Entity)
        for Entity in self.EntryFields:
            if Entity not in self.Gui.EntryFields:
                self.Gui.EntryFields.append(Entity)
        for Entity in self.Texts:
            if Entity not in self.Gui.Texts:
                self.Gui.Texts.append(Entity)
        for Entity in self.Buttons:
            if Entity not in self.Gui.Buttons:
                self.Gui.Buttons.append(Entity)
        for Entity in self.Images:
            if Entity not in self.Gui.Images:
                self.Gui.Images.append(Entity)

    def LeaveGui(self):
        for Entity in self.Scrolls:
            if Entity in self.Gui.Scrolls:
                self.Gui.Scrolls.remove(Entity)
        for Entity in self.Lines:
            if Entity in self.Gui.Lines:
                self.Gui.Lines.remove(Entity)
        for Entity in self.Rectangles:
            if Entity in self.Gui.Rectangles:
                self.Gui.Rectangles.remove(Entity)
        for Entity in self.EntryFields:
            if Entity in self.Gui.EntryFields:
                self.Gui.EntryFields.remove(Entity)
        for Entity in self.Texts:
            if Entity in self.Gui.Texts:
                self.Gui.Texts.remove(Entity)
        for Entity in self.Buttons:
            if Entity in self.Gui.Buttons:
                self.Gui.Buttons.remove(Entity)
        for Entity in self.Images:
            if Entity in self.Gui.Images:
                self.Gui.Images.remove(Entity)
